"""
Improved pipeline using state-of-the-art prompting techniques:
- Chain-of-Thought planning (ReAct inspired)
- Self-repair of SQL (Reflexion / Self-Refine)
- Stricter JSON evaluation
- SQL caching
- Timing of full pipeline per rule
"""

import time
import pandas as pd
import json
import sys
from typing import Any, Dict
from langchain.schema import SystemMessage, HumanMessage
from pipeline_helpers import get_llm
from db_utils import get_connection, run_query

# Cache dict to avoid regenerating SQL for the same rule
SQL_CACHE = {}

# ------------------------------------------------------------------------
# 1) Generate a PostGIS SQL query (planning + self-repair)
# ------------------------------------------------------------------------
def generate_postgis_query(
    csv_path: str,
    rule_text: str,
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> str:
    """
    Uses a planning step inspired by ReAct (Yao et al. 2022),
    followed by self-repair inspired by Reflexion / Self-Refine.
    """

    if rule_text in SQL_CACHE:
        return SQL_CACHE[rule_text]

    df = pd.read_csv(csv_path)

    schema_desc = """
        Table name: room_objects
        Columns:
        - id INTEGER
        - ifc_type TEXT
        - name TEXT
        - ifc_globalid TEXT
        - bbox GEOMETRY  -- stored as hex-encoded WKB
    """

    # 1: Planning step
    planning_system = SystemMessage(content=(
        "You are a spatial planning expert. Think step-by-step about "
        "which objects and spatial relationships are needed to check the rule. "
        "Return only a short plan."
    ))
    planning_human = HumanMessage(content=f"Rule: \"{rule_text}\". Provide plan only.")

    plan = client.invoke([planning_system, planning_human], model=model).content.strip()

    # 2: SQL generation step
    sql_system = SystemMessage(content=(
        "You are a PostGIS expert. Produce a single SQL SELECT query using the "
        "schema below and the provided plan. Return ONLY the SQL (no markdown)."
    ))
    sql_human = HumanMessage(content=f"""
        Schema:
        {schema_desc}

        Plan:
        {plan}

        Rule:
        \"{rule_text}\"
    """)
    sql_query = client.invoke([sql_system, sql_human], model=model).content.strip()

    # 3: Self-repair loop (Reflexion style)
    conn = get_connection()
    try:
        run_query(conn, sql_query)
    except Exception as e:
        repair_human = HumanMessage(content=f"""
            The following SQL caused an error in PostgreSQL:
            {sql_query}

            Error: {str(e)}

            Please correct the SQL and return ONLY the fixed version.
        """)
        sql_query = client.invoke([sql_system, repair_human], model=model).content.strip()

    SQL_CACHE[rule_text] = sql_query
    return sql_query


# ------------------------------------------------------------------------
# 2) Evaluate the query results (strict JSON enforced)
# ------------------------------------------------------------------------
def evaluate_query_results(
    query: str,
    results,
    rule_text: str,
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> Dict[str, Any]:
    """
    Enforces a strict JSON-object return using OpenAI-style function-prompting techniques.
    """
    system = SystemMessage(content=(
        "You are a spatial-reasoning assistant. "
        "Return ONLY a JSON object with EXACTLY these keys:\n"
        "  overall_compliant (boolean)\n"
        "  overall_explanation (string)"
    ))

    human = HumanMessage(content=f"""
        SQL executed:
        {query}

        Result rows:
        {results}

        Health & Safety Rule:
        \"{rule_text}\"

        Return exactly:
        {{
          "overall_compliant": true|false,
          "overall_explanation": "<one sentence reasoning>"
        }}
    """)

    ai_msg = client.invoke([system, human], model=model)
    try:
        return json.loads(ai_msg.content.strip())
    except json.JSONDecodeError:
        return {
            "overall_compliant": None,
            "overall_explanation": ai_msg.content.strip()
        }


# ------------------------------------------------------------------------
# 3) Main
# ------------------------------------------------------------------------
def main():
    llm = get_llm()
    csv_path = r"C:\Users\andri\Desktop\SMAPS\SMAPS\validation\r2m_db_full_data.csv"

    results_store = {}
    correct_count  = 0
    incorrect_count = 0

    timing_per_rule = {}

    conn = get_connection()

    for rule_id, gs in gold_standard.items():
        question       = gs["rule_text"]
        gs_compliant   = gs["overall_compliant"]
        gs_explanation = gs["explanation_summary"]

        print(f"\n▶️  Processing {rule_id}…")

        start_time = time.time()  # <- start stopwatch

        # 1) Generate/refine SQL
        sql = generate_postgis_query(csv_path, question, client=llm)
        print("   SQL:", sql)

        # 2) Execute SQL
        try:
            query_results = run_query(conn, sql)
        except Exception as e:
            print(f"⚠️  Query failed for {rule_id}: {e}", file=sys.stderr)
            query_results = []

        # 3) Evaluate
        evaluation = evaluate_query_results(
            query=sql,
            results=query_results,
            rule_text=question,
            client=llm
        )

        llm_compliant   = evaluation.get("overall_compliant")
        llm_explanation = evaluation.get("overall_explanation", "")

        # 4) Record correctness
        is_correct = (llm_compliant == gs_compliant)
        if is_correct:
            correct_count += 1
        else:
            incorrect_count += 1

        # 5) Stop timer
        end_time = time.time()
        elapsed = end_time - start_time
        timing_per_rule[rule_id] = elapsed

        # 6) Store result
        results_store[rule_id] = {
            "rule_text":         question,
            "generated_sql":     sql,
            "llm_compliant":     llm_compliant,
            "llm_explanation":   llm_explanation,
            "gold_compliant":    gs_compliant,
            "gold_explanation":  gs_explanation,
            "correct":           is_correct,
            "execution_time_sec": elapsed
        }

    # -------------------- summary --------------------
    total_time = sum(timing_per_rule.values())
    avg_time   = total_time / len(timing_per_rule)
    max_rule   = max(timing_per_rule, key=timing_per_rule.get)
    min_rule   = min(timing_per_rule, key=timing_per_rule.get)

    summary_block = {
        "correct_count":   correct_count,
        "incorrect_count": incorrect_count
    }

    execution_time_block = {
        "total_time_sec": total_time,
        "average_time_sec": avg_time,
        "max_time_rule": max_rule,
        "max_time_sec": timing_per_rule[max_rule],
        "min_time_rule": min_rule,
        "min_time_sec": timing_per_rule[min_rule]
    }

    final_output = {
        "results": results_store,
        "summary": summary_block,
        "execution_time": execution_time_block
    }

    out_path = "method2_results_improved.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done. {correct_count} correct, {incorrect_count} incorrect.")
    print("Execution-time summary:", execution_time_block)
    print(f"Results saved to {out_path}")


# ------------------------------------------------------------------------
# 4) Gold standard for the test
# ------------------------------------------------------------------------
if __name__ == "__main__":
    gold_standard = {
        "extinguisher_check1": {
            "rule_text": "Is access to portable fire extinguishers free from obstruction by nearby items?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
        },
        "extinguisher_check2": {
            "rule_text": "Have portable fire extinguishers been safely mounted to walls or placed on proper stands?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
        },
        "extinguisher_check3": {
            "rule_text": "Is the labelling on all portable fire extinguishers clear and visible?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
        },
        "fire_call_check": {
            "rule_text": "Is signage at all fire alarm call points clearly visible, and are these points easy to reach?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
        },
        "fire_escape_check1": {
            "rule_text": "Are signs marking fire exits placed appropriately and clearly noticeable at all times?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
        },
        "door_check": {
            "rule_text": "Is each fire door completely shut and not held open?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
        },
        "waste_check": {
            "rule_text": "Are waste materials and rubbish placed exclusively within their designated spaces?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
        },
        "ignition_check": {
            "rule_text": "Are all combustible items kept at a safe distance from ignition points?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
        },
        "fire_escape_check2": {
            "rule_text": "Is there any obstruction blocking fire escape routes?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
        },
        "fall_check": {
            "rule_text": "Is the walkway clear of objects that could obstruct passage?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
        }
    }
    main()