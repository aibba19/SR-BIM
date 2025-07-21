import json
import re
from typing import Dict, List, Tuple

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


def spatial_planner(
    checks_json: Dict,
    template_catalogue: Dict[str, str],
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> Dict:
    """
    Build a spatial-query plan from enriched checks.

    Returns:
      {"plans": [...]} according to the schema in the task.
    """
    # Normalize checks to list
    checks_list = checks_json.get("checks", []) if isinstance(checks_json, dict) else checks_json

    # Prepare serialized inputs
    checks_str = json.dumps(checks_list, indent=2, ensure_ascii=False)
    templates_md = "\n".join(
        f"- **{name}**: {desc}" for name, desc in template_catalogue.items()
    )

    # Task description (system message)
    # Task description (system message)
    base_prompt = """
    <task>
    You will decide which template relations must be run for each check.

    Input
      • <checks_json>: result of the previous step (reference, against, relation,
        plus resolved IDs or IFC types).
      • <template_catalogue>: list of available 1-to-1 template predicates.

    Rules
      1. Use only **templates** for every relation.

      2.  Example:  If and only if we have to test "unobstructed_by" or "visibility" related to an object, run "touches", then
         "front/right/left/behind/above/below".

         If and only if we have to test if a door it's open check containment against walls.
         If and only if we have to test if there is object on another just check "on top" relation

      2. When "against" or "reference" has "type":"any", indicate
           "b_source": "any_nearby"   or "a_source": "any_nearby"
         meaning the template will be executed later against *every* object found
         near the reference object.
      3. Preserve the order of checks.  Add a "check_index" so downstream code
         can align plan ↔ check.
      4. Return valid JSON **exactly** in the schema below.  No markdown.
      5. For each plan entry, include a field "relation_text" containing the
         original natural-language relation from the check (the value of the
         "relation" property).
      6. Always include some relations

    Output schema
    {{
      "plans": [
        {{
          "check_index": <int>,
          "reference": {{ ... same as input ... }},
          "against"  : {{ ... same as input ... }},
          "templates": [
            {{
              "template": "<template-name>",
              "a_source": "reference_ids|reference_ifc_types|any_nearby",
              "b_source": "against_ids|against_ifc_types|any_nearby"
            }},
            ...
          ]
        }},
        ...
      ]
    }}
    </task>
    """

    '''
        General guidance: When trying to understand **where an object is placed** or **how it relates spatially to others**, 
               it is often necessary to test **multiple spatial relations** to capture the full 
               surrounding context. Therefore, it is recommended to include **a broader set of spatial templates and object targets** 
               rather than a minimal set. This ensures more robust results and reduces the risk of missing relevant spatial conditions. 
               Including *more* relations and tested objects is preferred over *too few*.
        '''

    # Build prompt template
    prompt_template = ChatPromptTemplate(
        input_variables=["templates_md", "checks_str"],
        messages=[
            SystemMessagePromptTemplate.from_template(base_prompt),
            HumanMessagePromptTemplate.from_template(
                "<template_catalogue>\n{templates_md}\n</template_catalogue>\n\n"
                "<checks_json>\n{checks_str}\n</checks_json>"
            ),
        ],
    )

    # Format and invoke
    prompt_val = prompt_template.format_prompt(
        templates_md=templates_md,
        checks_str=checks_str
    )
    messages = prompt_val.to_messages()
    result = client.invoke(messages, model=model)

    # Extract content
    content = getattr(result, "content", str(result)).strip()
    if content.startswith("```"):
        content = re.sub(r"```json\s*|\s*```", "", content, flags=re.IGNORECASE).strip()

    # Parse and return
    try:
        print(content)
        return json.loads(content)
    except json.JSONDecodeError:
        # Attempt simple cleanup
        cleaned = re.sub(r",\s*(?P<closing>[\]\}])", r"\g<closing>", content)
        return json.loads(cleaned)


    