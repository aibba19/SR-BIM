import json
import re
from typing import List, Dict, Any

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def evaluate_rule(
    rule: str,
    summaries: List[str],
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> Dict[str, Any]:
    """
    Given a rule and spatial-check summaries, judge compliance and explain.

    Returns:
      {
        "entry_results": [{"summary":..., "compliant": true|false|null, "explanation":...}, ...],
        "overall_compliant": true|false,
        "overall_explanation": "..."
      }
    """
    # Serialize summaries as bullet list
    summaries_md = "\n".join(f"- {s}" for s in summaries)

    # Full task prompt (unchanged)
    task_prompt = """
        <task_description>
        You must judge whether a health-and-safety rule is met, using only the
        spatial-query *summaries* provided.

        ● Each summary describes:
           – which reference objects were tested,
           – which other objects are (or are not) in specific spatial relations,
           – and, by omission, which reference objects had **no matches** for the relation.

        ● Treat every spatial result as geometrically correct, but you may question the
          relevance of specific objects to the rule. If a match seems questionable or
          misaligned with the rule intent, describe the issue.

        Instructions:

        1. For **each** summary:
           – Write a clear and concise **explanation** of what the summary shows in relation to
             the rule. Describe:
               • Which reference objects satisfy the condition,
               • Which violate it,
               • Which may be in doubt (and why: unclear naming, ambiguous role, etc.).
           – When citing objects, always use both the **original name and ID** (e.g., `"Extg_03" (ID=107)`), especially when highlighting violations or unclear situations.
           – Do **not** assign a compliance label per summary—just explain the relevant facts
             in relation to the rule.

           The goal is to expose:
             – violations (who breaks the rule, and how),
             – satisfying cases (who is fine and why),
             – uncertainties (who/what needs follow-up and why).

        2. Use these explanations to give a final judgment:

           "overall_compliant" is **true** only if no object violates the rule and all
           ambiguities are minor or irrelevant.

           In "overall_explanation", combine the evidence from the summaries. Cite object
           **names and IDs** that cause violations or raise doubt, and explain why the rule
           is or isn’t respected overall.

        Return valid **JSON only**, in exactly this shape:

        {{
          "entry_results": [
            {{
              "summary": "<original summary>",
              "explanation": "<short reason>"
            }},
            …
          ],
          "overall_compliant": true | false,
          "overall_explanation": "<Overall reason>"
        }}
        </task_description>
        """

    # Human message with inputs appended after the task description
    human_template = (
        f"{task_prompt}\n\n"
        "<rule>\n{rule}\n</rule>\n\n"
        "<summaries>\n{summaries_md}\n</summaries>"
    )

    # Build prompt template
    prompt_template = ChatPromptTemplate(
        input_variables=["rule", "summaries_md"],
        messages=[
            SystemMessagePromptTemplate.from_template("Return valid JSON only."),
            HumanMessagePromptTemplate.from_template(human_template),
        ],
    )

    # Render and invoke LLM
    rendered = prompt_template.format_prompt(
        rule=rule,
        summaries_md=summaries_md
    ).to_messages()
    result = client.invoke(rendered, model=model)

    # Extract and clean output
    content = getattr(result, "content", str(result)).strip()
    if content.startswith("```"):
        content = re.sub(r"```json\s*|\s*```", "", content, flags=re.IGNORECASE).strip()

    # Parse JSON and return
    return json.loads(content)