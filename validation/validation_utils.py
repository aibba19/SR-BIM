import json
import csv
from typing import Dict, Any
from pipeline_helpers import get_llm
from langchain.schema import SystemMessage, HumanMessage

def explanation_match(
    llm,
    llm_explanation: str,
    gold_explanation: str,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> bool:
    """
    Ask the LLM to decide whether `llm_explanation` matches `gold_explanation`
    in terms of content and referenced objects. Returns True/False.
    """
    print ("LLM EXPLANATION : " + llm_explanation)
    print ("GOLD EXPLANATION : " + gold_explanation)

    system = SystemMessage(content=(
        "You are an assistant that compares two explanations of the same rule. "
        "Return only 'true' if they match in objects referenced and in spatial relation, "
        "otherwise return 'false'."
    ))

    human = HumanMessage(content=f"""
        Here are two explanations for the same health & safety rule.

        **LLM explanation**:
        \"\"\"{llm_explanation}\"\"\"

        **Gold explanation (reference standard)**:
        \"\"\"{gold_explanation}\"\"\"

        The gold explanation is the correct and trusted reference. Your task is to determine whether the LLM explanation conveys the same meaning and references the same objects and relationships.

        If the LLM explanation discusses the **same objects** and describes **similar spatial or functional relationships** between them as the gold explanation, respond with `true`.

        If it refers to **different objects** or relationships, or misunderstands the situation compared to the gold standard, respond with `false`.

        Respond with exactly `true` or `false`.
        """)

    ai_msg = llm.invoke([system, human],model=model)
    resp = ai_msg.content.strip().lower()

    print("RESPONSE: " + resp )
    return resp == "true"

def write_compliance_table(results: Dict[str, Any], output_csv: str):
    """
    Given a `results` dict formatted as in the prompt, write a CSV with columns:
      1) Rule Text
      2) Is the rule compliant for the method?
      3) Gold Compliant
      4) Compliance Match
      5) Explanation Match
    """
    llm = get_llm()
    fieldnames = [
        "Rule Text",
        "Is Compliant",
        "Gold Compliant",
        "Compliance Match",
        "Explanation Match"
    ]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for rule_id, entry in results.items():
            rule_text      = entry["rule_text"]
            llm_compliant  = entry.get("llm_compliant")
            gold_compliant = entry.get("gold_compliant")
            # 4) Compliance Match
            compliance_match = (llm_compliant is True and gold_compliant is True) or \
                               (llm_compliant is False and gold_compliant is False)
            # 5) Explanation Match
            if not compliance_match:
                explanation_match_flag = False
            else:
                llm_expl  = entry.get("llm_explanation", "")
                gold_expl = entry.get("gold_explanation", "")
                explanation_match_flag = explanation_match(
                    llm, llm_expl, gold_expl
                )

            writer.writerow({
                "Rule Text":           rule_text,
                "Is Compliant":        llm_compliant,
                "Gold Compliant":      gold_compliant,
                "Compliance Match":    compliance_match,
                "Explanation Match":   explanation_match_flag
            })

if __name__ == "__main__":
    # Load your results from JSON (or replace this with the dict directly)
    with open("method1_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    results = data["results"]

    # Write out the comparison table
    write_compliance_table(results, "compliance_comparison_method1.csv")
    print("✅ compliance_comparison.csv written")