import json
import re
from typing import Dict

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def decompose_rule(hs_rule: str, client, model: str = "gpt-4.1-mini-2025-04-14") -> Dict:
    """
    Decompose a single health-and-safety rule into atomic checks.
    """
    # Full task text (unchanged)
    prompt_text = """
        <task>
        You will convert one health-and-safety rule into a JSON plan for later spatial checks.

        Output **JSON only**:
        {{
          "checks": [
            {{
              "reference": {{ "type": "<object|category|any>", "value": "<text>" }},
              "relation" : "<canonical_relation>",
              "against"  : {{ "type": "<object|category|any>", "value": "<text>" }}
            }},
            …
          ]
        }}

        Guidelines
        1. Split the rule into the **smallest meaningful checks**—there may be one or many.
        2. Always Identify the **reference**: the primary object or category whose spatial relation you will **test**.
        3. Always Identify the **against**: the secondary object or category **serving as context** for that test.
        4. Always choose reference and against by logical role in the clause—reference is the subject being evaluated, against is the target it’s checked against and can also be inferred if not explicit in the rule.
        5. Use **type = "object"** for specific items (“fire extinguisher”), **"category"** for general groups (“stored items”, “obstacles”).
        6. Pick a concise **relation** string that captures how reference and against relate.
        7. Do **not** invent extra checks or duplicate identical reference/against pairs.
        8. If the rule implies “free of any obstruction / any item”, set {{ "type": "any", "value": "any object" }}.
        9. If the rule says “on” something, use the relation `"on_top_of"`.
        10. Return valid JSON only—no markdown, no code fences, no extra keys.
        </task>
        """

    # Append the actual rule
    human_content = f"{prompt_text}\n<rule>{hs_rule}</rule>"

    # Build a ChatPromptTemplate with a single system + single human message
    prompt_template = ChatPromptTemplate(
        input_variables=["hs_rule"],
        messages=[
            SystemMessagePromptTemplate.from_template("Return valid JSON only."),
            HumanMessagePromptTemplate.from_template(human_content),
        ],
    )

    # Render and invoke
    rendered = prompt_template.format_prompt(hs_rule=hs_rule).to_messages()
    result = client.invoke(rendered, model=model)

    # Clean and parse
    content = getattr(result, "content", str(result))
    if content.startswith("```"):
        content = re.sub(r"```json\s*|```\s*$", "", content, flags=re.IGNORECASE).strip()

    return json.loads(content)