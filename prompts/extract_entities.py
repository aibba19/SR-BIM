import json
import re
from typing import Dict, List, Tuple

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# Entities matching
def extract_entities(
    rule_json: Dict,
    user_defined_types: List[str],
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> Dict:
    """
    Enriches a decomposed H&S rule with concrete object IDs or IFC-type categories.

    Returns same structure as input, but each check gains:
      - "reference_ids": [ids...] or
      - "against_ids": [ids...] or
      - "reference_ifc_types" / "against_ifc_types": [types...]
    """
    # Prepare serialized inputs
    checks_str = json.dumps(rule_json.get("checks", []), indent=2, ensure_ascii=False)
    user_defined_types_md = "\n".join(f"- {t}" for t in sorted(set(user_defined_types)))

    # Full task prompt (unchanged)
    prompt_text = """
        <task>
        Map every *reference* and *against* entry in <checks> to one or more object
        types chosen **only** from <available_objects>.

        Matching rules
        • For values whose "type" is either **"object"** or **"category"**, add
          `"reference_ifc_types"` / `"against_ifc_types"` containing **all** object types
          from <available_objects> that logically match that value (synonyms and
          common usage allowed, case-insensitive).  Include multiple types whenever
          more than one class is relevant.
        • If "type" is "any"   ⟶  set the field to ["any"] (meaning all types).

        Constraints
        • Use **only** the IFC types listed in <available_ifc_types>.
          Never invent new strings.
        • Err on the side of inclusion: when unsure, keep a broader set rather
          than a restrictive one.
        • Leave all other fields unchanged.
        • Return **valid JSON only** (no markdown, code fences, or extra keys).
        </task>
        """
    #• Err on the side of inclusion: when unsure, keep a broader set rather
    #      than a restrictive one.

    # Build the prompt template
    prompt_template = ChatPromptTemplate(
        input_variables=["checks_str", "objects_md"],
        messages=[
            SystemMessagePromptTemplate.from_template("Return valid JSON only."),
            HumanMessagePromptTemplate.from_template(
                prompt_text +
                "\n<checks>\n{checks_str}\n</checks>\n\n"
                "<available_objects>\n{user_defined_types_md}\n</available_objects>"
            ),
        ],
    )

    # Format and call LLM
    rendered = prompt_template.format_prompt(
        checks_str=checks_str,
        user_defined_types_md=user_defined_types_md
    ).to_messages()
    result = client.invoke(rendered, model=model)

    # Clean response
    content = getattr(result, "content", str(result)).strip()
    if content.startswith("```"):
        content = re.sub(r"```json\s*|```", "", content, flags=re.IGNORECASE).strip()

    #print(content)

    # Parse and return
    return json.loads(content)

