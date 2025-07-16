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

    # Full task prompt
    prompt_text = """
        <task>
        Map every *reference* and *against* entry in <checks> to one or more object types
        chosen **only** from <available_objects>.

        Matching logic
        --------------
        • For entries whose `"type"` is **"object"** or **"category"**:
          1. Each UDT in <available_objects> is structured as  
             `IfcType_mainName_extraInfo` (extraInfo is optional).
          2. Match if **mainName** (or its synonyms/common variants) corresponds to the
             entry’s `"value"`.
          3. Use **IfcType** to filter broad classes (e.g. all `IfcFurnishingElement_*`
             for furnishing-related checks or stored items).
          4. Use **extraInfo** to refine: exclude UDTs whose extraInfo clearly contradicts
             the intended meaning.
          5. Matching is semantic and case-insensitive.  
          6. Include **all** matching UDTs; when uncertain, err on the side of inclusion.
          7. to test if a door it's open check containment against walls.

        • If `"type"` is **"any"**, set  
          `"reference_ifc_types"` / `"against_ifc_types"` → `["any"]`.

        • Paper and plants are combustible materials
        • IfcElectricDistributionPoint are source of ignition
        • To check if there are trip hazard we have to use walkways as reference and any as against
        • Consider fire escape routes the fire exit doors

        

        Constraints
        -----------
        • Use **only** UDTs in <available_objects>; never invent new strings.  
        • Preserve every other field exactly as-is.  
        • Return **valid JSON only** (no markdown, code fences, or extra keys).
        
        </task>
        """
    

    #Examples already present in the data set:

    #            • IfcFurnishingElement_Stock of Paper  
    #        • IfcFurnishingElement_small plant_Ny märkning  
    #        • IfcFurnishingElement_Fire Extinguisher Label
    '''
    – *Example*:  
               Value = "combustible materials" → select any UDT whose keywords denote  
               items that fit the **Combustible Materials** definition above  
               (e.g. “Stock of Paper”), but **exclude** benign or non-flammable items  
               (e.g. “Fire Extinguisher Label”).

    • **Never output an empty list.** Each `"reference_ifc_types"` or `"against_ifc_types"`
            must contain **at least one** UDT; when unsure, a broader set is better than none. 
    '''

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

