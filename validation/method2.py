import pandas as pd
import json
import sys
from typing import Any, Dict
from langchain.schema import SystemMessage, HumanMessage
from pipeline_helpers import get_llm
from db_utils import get_connection, run_query
import time  

# ------------------------------------------------------------------------
# 1) Generate a PostGIS SQL query for a given rule
# ------------------------------------------------------------------------
def generate_postgis_query(
    csv_path: str,
    rule_text: str,
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> str:
    """
    Reads the CSV schema and asks the LLM to write a single PostGIS SQL
    SELECT that extracts exactly the data needed to evaluate `rule_text`.
    Returns only the SQL query string.
    """
    # 1. Load and serialize full db data if needed
    df = pd.read_csv(csv_path)
    csv_text = df.to_csv(index=False)

    # We only need the schema here, not the full data
    schema_desc = """
        Table name: room_objects
        Columns:
        - id INTEGER
        - ifc_type TEXT
        - name TEXT
        - ifc_globalid TEXT
        - bbox GEOMETRY  -- stored as hex-encoded WKB
        """
    system = SystemMessage(content=(
        "You are a database expert in PostgreSQL/PostGIS. "
        "I will give you a table schema and a health & safety rule.  "
        "Write a **valid** SQL statement that can be run directly "
        "in psycopg2 or similar.  **Return only the SQL** (no markdown, no comments, "
        "no explanation).  It must end with a semicolon, "
        "and use only the columns appropriate to the schema."
        "The objective of the generated SQL is to retrieve a broad set of data that is as comprehensive as possible in relation to the question. "
        "Therefore, avoid applying complex filters or operations, and ensure that the query returns relevant data that can be evaluated in a later step to answer the question."
    ))

    human = HumanMessage(content=f"""
        {schema_desc}

        **Health & Safety Rule**:
        \"\"\"{rule_text}\"\"\"

        Write a PostgreSQL/PostGIS query using any relevant spatial or SQL functions to extract the data required to evaluate compliance with the above rule.

        Each object in the environment is represented by its bounding box in a 3D internal space.

        The goal is to identify all **relevant objects** involved in the rule and retrieve **spatial relationships or properties** that can later be used to assess compliance.

        You are not expected to directly answer the rule in this query. Instead, construct a query that returns:
        - All candidate objects involved in the rule.
        - Any other objects that are spatially related to them (e.g., near, touching, above, contained in, etc.).
        - Geometric or spatial values that can help further evaluate these relationships in a subsequent reasoning step.

        Focus on retrieving data that can support later compliance evaluation keeping the query simple.

        """)

    #Full database dump : 
    
    #{csv_text}
    
    # invoke the LLM
    ai_msg = client.invoke([system, human], model=model)
    return ai_msg.content.strip()

# ------------------------------------------------------------------------
# Helper: Ask LLM to fix a failing SQL using the DB error message
# (Inspired by Self-Refine / Reflexion: iterative self-correction)
# ------------------------------------------------------------------------
def repair_sql_with_llm(failing_sql: str, error_text: str, client, model: str = "gpt-4.1-mini-2025-04-14") -> str:
    system = SystemMessage(content=(
        "You are a PostgreSQL/PostGIS expert. I will give you a SQL query that failed, "
        "and the exact error message from the database. Return ONLY a corrected SQL statement "
        "that resolves the error. No prose, no markdown, end with a semicolon."
    ))
    human = HumanMessage(content=f"""
        Failing SQL:
        {failing_sql}

        Error:
        {error_text}

        Return only the corrected SQL. Simplify the SQL so that you are sure that will run.
    """)
    ai_msg = client.invoke([system, human], model=model)
    return ai_msg.content.strip()

# ------------------------------------------------------------------------
# 2) Evaluate the query results to answer the rule
# ------------------------------------------------------------------------
def evaluate_query_results(
    query: str,
    results,
    rule_text: str,
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> Dict[str, Any]:
    """
    Given the SQL that was run, and its results as a DataFrame,
    ask the LLM to decide `overall_compliant` and supply an
    `overall_explanation` in structured JSON.

    If the LLM call fails for any reason, catch the error and
    return it in the 'overall_explanation' field instead of raising.
    """

    print("Result : " + str(results))

    system = SystemMessage(content=(
        "You are a spatial-reasoning assistant. Analyze the provided query results "
        "and return *only* a JSON object with exactly two keys:\n"
        "  overall_compliant  – true or false\n"
        "  overall_explanation – a paragraph explaining which objects (name+ID) "
        "you examined, what spatial relation you found, and why the rule is satisfied or violated."
    ))

    human = HumanMessage(content=f"""
        The following SQL was run to extract the relevant data:

        ```sql
        {query}
        Here are the results of that query (columns as returned):

        {results}

        Health & Safety Rule:
        \"\"\"{rule_text}\"\"\"

        Please answer strictly based on the data above, and return only this JSON:
        {{
          "overall_compliant": true|false,
          "overall_explanation": "<which objects (name+ID) you checked, their spatial relation, and exactly why the rule holds or is violated>"
        }}
    """)

    try:
        ai_msg = client.invoke([system, human], model=model)
    except Exception as e:
        # Catch *any* error from the LLM call and return it
        return {
            "overall_compliant": None,
            "overall_explanation": f"⚠️ LLM call failed: {str(e)}"
        }

    # Try to parse the response
    try:
        return json.loads(ai_msg.content.strip())
    except json.JSONDecodeError:
        # propagate raw content if parsing fails
        return {
            "overall_compliant": None,
            "overall_explanation": ai_msg.content.strip()
        }

def main():
    llm = get_llm()
    csv_path = r"C:\Users\andri\Desktop\SMAPS\SMAPS\validation\room2-r2m-room-objects-bbox.csv"

    results = {}
    correct_count = 0
    incorrect_count = 0
    returned_results = []   # <--- track results per rule

    conn = get_connection()

    for rule_id, gs in gold_standard.items():
        question       = gs["rule_text"]
        gs_compliant   = gs["overall_compliant"]
        gs_explanation = gs["explanation_summary"]

        print(f"▶️  Processing {rule_id}…")

        start_time = time.time()  # <-- START TIME FOR THIS RULE

        # 1) Ask LLM to generate the PostGIS query
        sql = generate_postgis_query(csv_path, question, client=llm)
        print(f"   Generated SQL: {sql}")

        # 2) Run that query against your database (with self-repair on error)
        try:
            query_results = run_query(conn, sql)
        except Exception as e:
            print(f"⚠️  Query failed for {rule_id}: {e}", file=sys.stderr)

            # --- Self-repair loop (up to 2 attempts). Inspired by Self-Refine / Reflexion ---
            max_fixes = 2
            fixed = False
            last_error = str(e)
            for attempt in range(1, max_fixes + 1):
                print(f"   🔧 Attempting SQL auto-repair {attempt}/{max_fixes} …")
                repaired_sql = repair_sql_with_llm(sql, last_error, client=llm)
                print(f"   Repaired SQL: {repaired_sql}")
                try:
                    query_results = run_query(conn, repaired_sql)
                    sql = repaired_sql  # keep the fixed SQL
                    fixed = True
                    print("   ✅ Repair successful.")
                    break
                except Exception as e2:
                    last_error = str(e2)
                    print(f"   ❌ Repair attempt {attempt} failed: {last_error}", file=sys.stderr)

            if not fixed:
                # fallback: empty results if still failing
                print("   ⚠️ Using empty results after failed repairs.", file=sys.stderr)
                query_results = []

        # Track if results were returned
        returned_results.append({
            "id": rule_id,
            "Results": bool(query_results)  # True if not empty, False otherwise
        })

        # 3) Ask LLM to evaluate the query results
        evaluation = evaluate_query_results(
            query=sql,
            results=query_results,
            rule_text=question,
            client=llm
        )
        llm_compliant   = evaluation.get("overall_compliant")
        llm_explanation = evaluation.get("overall_explanation", "")

        # 4) Compare to gold standard
        is_correct = (llm_compliant is True and gs_compliant is True) or \
                     (llm_compliant is False and gs_compliant is False)
        if is_correct:
            correct_count += 1
        else:
            incorrect_count += 1

        end_time = time.time()                    # <-- END TIME FOR THIS RULE
        elapsed = end_time - start_time

        # 5) Record results
        results[rule_id] = {
            "rule_text":         question,
            "generated_sql":     sql,  # note: stores repaired SQL if applicable
            "llm_compliant":     llm_compliant,
            "llm_explanation":   llm_explanation,
            "gold_compliant":    gs_compliant,
            "gold_explanation":  gs_explanation,
            "correct":           is_correct,
            "execution_time_sec": elapsed
        }

    # 6) Summaries
    output = {
        "results": results,
        "summary": {
            "correct_count":   correct_count,
            "incorrect_count": incorrect_count
        },
        "returned_results": returned_results   # <--- NEW ENTRY
    }

    # 7) Execution time summary block
    total_time = sum(r["execution_time_sec"] for r in results.values())
    avg_time   = total_time / len(results) if results else 0
    max_rule   = max(results, key=lambda k: results[k]["execution_time_sec"])
    min_rule   = min(results, key=lambda k: results[k]["execution_time_sec"])

    output["execution_time"] = {
        "total_time_sec": total_time,
        "average_time_sec": avg_time,
        "max_time_rule": max_rule,
        "max_time_sec": results[max_rule]["execution_time_sec"],
        "min_time_rule": min_rule,
        "min_time_sec": results[min_rule]["execution_time_sec"]
    }

    out_path = "method2_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. {correct_count} correct, {incorrect_count} incorrect.")
    print("Execution-time summary:", output["execution_time"])
    print(f"Results saved to {out_path}")



if __name__ == "__main__":
    

    #Romm2 E Version 
    gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Do furnishings or stored equipment obstruct easy access to fire extinguishing canisters?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are not obstructed by any nearby stored items and are easily accessible."
    },
    "extinguisher_check2": {
        "rule_text": "Are all extinguishers either properly fixed to structural surfaces or resting on approved holders?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are properly affixed to a wall or mounted on an appropriate stand."
    },
    "extinguisher_check3": {
        "rule_text": "Do the fire extinguishing tools display visible identification tags?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111), and extinguishers (IDs 2, 3) are also in contact with clearly visible labels."
    },
    "fire_call_check": {
        "rule_text": "Are fire emergency activation points clearly marked and not obstructed?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because both fire alarm call points (IDs 113 and 115) are clearly signed and physically accessible."
    },
    "fire_escape_check1": {
        "rule_text": "Are fire direction signs properly located and clearly visible at all times?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because no fire exit sign is positioned correctly above the fire exit doors, failing visibility and placement requirements."
    },
    "door_check": {
        "rule_text": "Are all fire-resistance doors maintained in a fully shut position?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Door (ID:18) is sufficiently contained within its frame and surrounding wall, indicating it is closed."
    },
    "waste_check": {
        "rule_text": "Is trash stored in authorized containment zones?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because the Waste Bin (ID:10) is not properly placed within the designated Trash Disposal Area."
    },
    "ignition_check": {
        "rule_text": "Are fire-prone substances kept away from electrical sources?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because the combustible materials, such as plants (IDs 100, 101), are not near any ignition sources."
    },
    "fire_escape_check2": {
        "rule_text": "Is the emergency egress doors kept clear of physical barriers?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because a furnishing object (ID:98) is positioned directly in front of Fire Exit Door (ID:19), obstructing access, despite nearby extinguishers and HVAC devices not causing obstruction."
    },
    "fall_check": {
        "rule_text": "Are footpaths within the room free of any obstructions?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because no objects are located directly on the surface of walkway1 (ID:119), ensuring a clear walking path."
    }
}
    main()

    