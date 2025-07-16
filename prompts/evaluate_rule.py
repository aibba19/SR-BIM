import json
import re
import logging
from typing import List, Dict, Any

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

logger = logging.getLogger(__name__)

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
        "entry_results": [...],
        "overall_compliant": true|false,
        "overall_explanation": "..."
      }

    Raises:
      ValueError on JSON parse failure, including the raw content for debugging.
    """
    # Serialize summaries as bullet list
    summaries_md = "\n".join(f"- {s}" for s in summaries)

    # (task_prompt / prompt_template creation unchanged) ...
    task_prompt = """
        <task_description>
        Decide whether the health-and-safety <rule> is respected, using only the
        bullet-list <summaries> of spatial results.

        Instructions
        1. For each summary:
           • Explain in 1–2 sentences which reference objects (name + ID) and related
             objects confirm, violate, or cast doubt on the rule.
           • Note any uncertainties (unclear naming, role, or relation).

        2. Set "overall_compliant":
           • true  – no violations and only minor doubts.
           • false – any clear violation or significant doubt.

        3. Write "overall_explanation": a single paragraph citing key objects (name + ID)
           and relations that justify the verdict.

        4. For door objects, consider them **closed** if ≥ 80% of their volume is
            contained within the wall; while if it's less treat them as **open**.

        Output – JSON only
        {{  
          "entry_results": [
            {{ "summary": "<original summary>", "explanation": "<your explanation>" }}
          ],
          "overall_compliant": true | false,
          "overall_explanation": "<your paragraph>"
        }}
        Return nothing else (no markdown, code fences, or extra keys).
        </task_description>
        """
    human_template = (
        f"{task_prompt}\n\n"
        "<rule>\n{rule}\n</rule>\n\n"
        "<summaries>\n{summaries_md}\n</summaries>"
    )
    prompt_template = ChatPromptTemplate(
        input_variables=["rule", "summaries_md"],
        messages=[
            SystemMessagePromptTemplate.from_template("Return valid JSON only."),
            HumanMessagePromptTemplate.from_template(human_template),
        ],
    )
    rendered = prompt_template.format_prompt(
        rule=rule,
        summaries_md=summaries_md
    ).to_messages()
    result = client.invoke(rendered, model=model)

    # Clean markdown fences
    content = getattr(result, "content", str(result)).strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE | re.MULTILINE)

    # Try to parse, with fallback strategies
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning("Initial JSON parse failed: %s", e)

        # 1) Extract the first { … } block
        block_match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if block_match:
            candidate = block_match.group(0)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError as e2:
                logger.warning("Block‐extraction parse failed: %s", e2)

        # 2) Strip trailing commas before } or ]
        sanitized = re.sub(r",\s*([]}])", r"\1", content)
        try:
            return json.loads(sanitized)
        except json.JSONDecodeError as e3:
            logger.error("Sanitized parse failed: %s", e3)

        # If we get here, give up with raw content for inspection
        raise ValueError(
            "Failed to parse JSON response from LLM.\n"
            f"Original parse error: {e}\n"
            f"Raw content was:\n{content}\n"
        )