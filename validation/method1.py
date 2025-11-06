import pandas as pd
from typing import Any, Dict
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage, HumanMessage
from pipeline_helpers import get_llm, get_openrouter_llm
import json
import sys
import time

def analyze_health_safety(
    csv_path: str,
    health_safety_query: str,
    client,
    model: str = "gpt-4.1-mini-2025-04-14"
) -> str:
    """
    Reads the IFC-derived object table from a CSV, constructs a prompt
    instructing the LLM to decode bounding boxes, deduce 3D positions and
    spatial relations, then answer a health & safety question as structured JSON.
    """

    # 1. Load and serialize
    df = pd.read_csv(csv_path)
    csv_text = df.to_csv(index=False)

    # 2. Build the two messages directly
    system_content = (
        "You are an expert spatial-reasoning assistant. "
        "Analyze the provided data and return *only* a JSON object with exactly two keys: "
        "`overall_compliant` (true or false) and `overall_explanation` (a single paragraph explaining "
        "which objects (name + ID) you examined, what spatial relations you found, and why the rule "
        "is satisfied or violated)."
    )

    human_content = f"""
    We are providing you a CSV dump of objects derived from an IFC model, with schema:
    - id: integer identifier  
    - ifc_type: object class  
    - name: instance name  
    - ifc_globalid: IFC GUID  
    - bbox: hex-encoded WKB 3D polygon of its bounding box

    Your job:
    1. Decode each `bbox` into 3D coordinates.
    2. Compute each object’s position.
    3. Infer spatial relations (distance, adjacency, containment, etc.).
    4. Answer the question *strictly using that spatial reasoning*.

    **Question:** {health_safety_query}

    **Output JSON** (no markdown, no code fences, nothing else):
    ```json
    {{
      "overall_compliant": true|false,
      "overall_explanation": "<which objects (name + ID) you checked, their spatial relation, and exactly why the rule holds or is violated>"
    }}
    Here is the CSV (columns: id,ifc_type,name,ifc_globalid,bbox):
    {csv_text}
    """

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]

    # 3. Invoke
    response = client.invoke(messages, model=model)

    return response

def main():
    #This line use open ai 4.1 mini
    #llm = get_llm()
    #This line use the llm from openrouter defined in the function
    llm = get_openrouter_llm()

    csv_path = r"C:\Users\andri\Desktop\SMAPS\SMAPS\validation\room1-r2m_db_full_data.csv" # room2-r2m-room-objects-bbox

    results = {}
    correct_count = 0
    incorrect_count = 0
    exec_times = {}  # per-rule execution times (seconds)

    for rule_id, gs in gold_standard.items():
        start_t = time.perf_counter()  # ⏱ start timing this rule

        question       = gs["rule_text"]
        gs_compliant   = gs["overall_compliant"]
        gs_explanation = gs["explanation_summary"]

        print(f"▶️  Evaluating {rule_id}…")
        ai_msg = analyze_health_safety(
            csv_path=csv_path,
            health_safety_query=question,
            client=llm,
        )
        raw = ai_msg.content.strip()

        # parse LLM JSON
        try:
            parsed = json.loads(raw)
            llm_compliant   = parsed.get("overall_compliant")
            llm_explanation = parsed.get("overall_explanation", "")
        except json.JSONDecodeError:
            print(f"⚠️  JSON parse error for {rule_id}: {raw}", file=sys.stderr)
            llm_compliant   = None
            llm_explanation = raw

        # compare to gold standard
        is_correct = (llm_compliant is True  and gs_compliant is True) or \
                     (llm_compliant is False and gs_compliant is False)
        if is_correct:
            correct_count += 1
        else:
            incorrect_count += 1

        # ⏱ stop timing this rule
        duration = time.perf_counter() - start_t
        exec_times[rule_id] = duration

        # assemble result entry (include execution time)
        results[rule_id] = {
            "rule_text":         question,
            "llm_compliant":     llm_compliant,
            "llm_explanation":   llm_explanation,
            "gold_compliant":    gs_compliant,
            "gold_explanation":  gs_explanation,
            "correct":           is_correct,
            "execution_time_sec": duration
        }

    # execution-time summary
    total_time = sum(exec_times.values())
    avg_time = total_time / len(exec_times) if exec_times else 0.0
    max_rule = max(exec_times, key=exec_times.get) if exec_times else None
    min_rule = min(exec_times, key=exec_times.get) if exec_times else None

    # summary + dump
    output = {
        "results": results,
        "summary": {
            "correct_count":   correct_count,
            "incorrect_count": incorrect_count
        },
        "execution_time": {
            "total_time_sec": total_time,
            "average_time_sec": avg_time,
            "max_time_rule": max_rule,
            "max_time_sec": exec_times[max_rule] if max_rule else None,
            "min_time_rule": min_rule,
            "min_time_sec": exec_times[min_rule] if min_rule else None
        }
    }

    out_path = "method1_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. {correct_count} correct, {incorrect_count} incorrect.")
    print(f"⏱  Total: {total_time:.3f}s | Avg/check: {avg_time:.3f}s | "
          f"Max ({max_rule}): {exec_times[max_rule]:.3f}s | "
          f"Min ({min_rule}): {exec_times[min_rule]:.3f}s")
    print(f"Results saved to {out_path}")

if __name__ == "__main__":
    
    #A version room 1
    gold_standard = {
        "extinguisher_check1": {
            "rule_text": "Are all portable fire extinguishers readily accessible and not restricted by stored items?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
        },
        "extinguisher_check2": {
            "rule_text": "Are portable fire extinguishers either securely wall mounted or on a supplied stand?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
        },
        "extinguisher_check3": {
            "rule_text": "Are portable fire extinguishers clearly labelled?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
        },
        "fire_call_check": {
            "rule_text": "Are all fire alarm call points clearly signed and easily accessible?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
        },
        "fire_escape_check1": {
            "rule_text": "Are fire exit signs installed at the proper locations and remain clearly visible?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
        },
        "door_check": {
            "rule_text": "Are fire doors kept closed, i.e., not wedged open?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
        },
        "waste_check": {
            "rule_text": "Is waste and rubbish kept in a designated area?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
        },
        "ignition_check": {
            "rule_text": "Have combustible materials been stored away from sources of ignition?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
        },
        "fire_escape_check2": {
            "rule_text": "Are fire escape routes kept clear?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
        },
        "fall_check": {
            "rule_text": "Are there any objects on the walk path?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
        }
    }

    main()

