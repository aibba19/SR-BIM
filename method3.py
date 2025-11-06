from optparse import Option
from typing import Any, Dict, Optional, List, Literal, TypedDict
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
#from langgraph import PromptTemplate, LLMChain
from pipeline_helpers import *
from prompts.decompose_rule import decompose_rule
from prompts.extract_entities import extract_entities
from prompts.spatial_planner import spatial_planner
from prompts.decide_plan_polarity import decide_plan_polarity
from prompts.create_summaries import summarise_spatial_results
from prompts.evaluate_rule import evaluate_rule

import functools
from pathlib import Path
import time


# ──────────────────────────────────────────────────────────────────────────
#  Template catalogue  (key → SQL filename or None for composed funcs)
# ──────────────────────────────────────────────────────────────────────────
TEMPLATE_MAP: Dict[str, str | None] = {
    # 4‑param directionals
    "above": "above.sql",
    "below": "below.sql",
    "front": "front.sql",
    "behind": "behind.sql",
    "left": "left.sql",
    "right": "right.sql",
    # 3‑param distance
    "near": "near_far.sql",
    "far": "near_far.sql",
    # 2‑param boolean
    "touches": "touches.sql",
    # composed (executed in Python, no SQL file needed)
    "on_top_of": None,
    "leans_on": None,
    "affixed_to": None,
    "contains": "contains.sql"
}

# Turn every SQL filename into a Path for db_utils
TEMPLATE_PATHS = {
    k: (Path(__file__).with_suffix("").parent / "sql" / v) if v else None
    for k, v in TEMPLATE_MAP.items()
}

TEMPLATE_CATALOGUE = {
    "touches":    "True when two object bounding boxes are ≤ 0.1 m apart or intersect.",
    "front":      "True when A is in front of B, within a small distance threshold.",
    "behind":     "True when A is behind B, relative to the camera point of view, within a small threshold.",
    "left":       "True when A is to the left of B, within a small distance threshold.",
    "right":      "True when A is to the right of B, within a small distance threshold.",
    "above":      "True when A is above B, within a small distance threshold.",
    "below":      "True when A is below B, within a small distance threshold.",
    "on_top_of":  "True when A is placed directly on top of B.",
    "leans_on":   "True when A is supported by B.",
    "affixed_to": "True when A is affixed to B.",
    "near":       "True when the distance between A and B is less than a defined threshold.",
    #"far":        "True when the distance between A and B is greater than a defined threshold.",
    "contains":   "Check containment between A and B"
}

def prepare_template_paths() -> Dict[str, Path]:
    """
    Prepare and return a dictionary mapping template names to their SQL file paths.
    """
    SQL_DIR = Path(__file__).parent / "sql"
    print(f"DEBUG: SQL directory is {SQL_DIR}")
    template_paths: Dict[str, Path] = {
        name: (SQL_DIR / fname) for name, fname in TEMPLATE_MAP.items() if fname
    }
    print(f"DEBUG: Prepared template paths for {len(template_paths)} SQL files.\n")
    return template_paths

class PipeState(TypedDict):

    pov_id: int
    extrusion_factor_s: int
    tolerance_metre: float
    near_far_threshold: float

    rule_text: str
    decomposed_checks: Optional[dict]

    all_objects: Optional[List[Tuple[int, str, str]]]
    id_to_obj:   Optional[Dict[int, Tuple[str, str]]]
    all_ids:     Optional[List[int]]
    type_to_ids: Optional[Dict[str, List[int]]]

    user_defined_types :Optional[List[str]]
    udt_to_ids: Optional[dict]

    enriched_checks: Optional[dict]
    spatial_plan: Optional[dict]
    relations: Optional[Any]
    
    evaluation: Optional[dict]

class Evaluate_Hs_Rule:
    """
    A class for evaluating health and safety rules
    """
    def __init__(self, pov_id, extrusion_factor_s, tolerance_metre, near_far_threshold, model_name: str = "gpt-4.1-mini-2025-04-14"):
        self.llm = get_llm(model_name=model_name)
        self.chain = None
        self.build_workflow()
        self.pov_id = pov_id
        self.extrusion_factor_s = extrusion_factor_s
        self.tolerance_metre = tolerance_metre
        self.near_far_threshold = near_far_threshold

    def build_workflow(self):
        workflow = StateGraph(PipeState)

        workflow.add_node("decompose rule", self.decompose_rule)
        workflow.add_node("load Database objects", self.load_objects)
        workflow.add_node("create user defined types", self.extract_user_defined_types)
        workflow.add_node("match udts with rule entities", self.entities_matching)
        workflow.add_node("plan relation to be run", self.spatial_plan)
        
        workflow.add_node("execute planned relations", self.execute_planned_relations)

        #workflow.add_node("summarise results", self.summarise_results)

        workflow.add_node("evaluate results", self.evaluate_rule)

        workflow.add_edge(START,"load Database objects")
        workflow.add_edge("load Database objects", "create user defined types" )
        workflow.add_edge("create user defined types", "decompose rule" )
        workflow.add_edge("decompose rule", "match udts with rule entities")
        workflow.add_edge("match udts with rule entities", "plan relation to be run")

       
        workflow.add_edge("plan relation to be run","execute planned relations")

        workflow.add_edge("execute planned relations","evaluate results" )
        
        workflow.add_edge("evaluate results", END)

        self.workflow = workflow
        self.chain = workflow.compile()
        return self.chain

    def decompose_rule(self, state: PipeState) -> PipeState:
        state["decomposed_checks"] = decompose_rule(state["rule_text"], self.llm)
        return state

    def load_objects(self, state: PipeState) -> PipeState:
        all_objs, id2obj, ids, type2ids = load_objects_and_maps()
        state["all_objects"] = all_objs
        state["id_to_obj"] = id2obj
        state["all_ids"] = ids
        state["type_to_ids"] = type2ids
        return state

    def extract_user_defined_types(self, state:PipeState) -> PipeState:
        user_defined_types_list = extract_user_defined_types(state["all_objects"])
        state["user_defined_types"] = user_defined_types_list

        # 2) compute udt_to_ids once:
        udt_to_ids = ids_from_udts(user_defined_types_list, state["all_objects"])
        state["udt_to_ids"] = udt_to_ids

        return state

    def entities_matching(self, state: PipeState) -> PipeState:
        enriched = extract_entities(
            state["decomposed_checks"],
            state["user_defined_types"],
            self.llm
        )
        state["enriched_checks"] = enriched
        return state

    def spatial_plan(self, state: PipeState) -> PipeState:
        plan = spatial_planner(
            state["enriched_checks"],
            TEMPLATE_CATALOGUE,
            self.llm
        )
        state["spatial_plan"] = plan
        return state

    def decide_polarity(self, state: PipeState) -> PipeState:
        decisioned = decide_plan_polarity(
            state["rule_text"],
            state.get("spatial_plan", {}),
            self.llm
        )
        state["spatial_plan"] = decisioned
        return state

    def execute_planned_relations(self, state: PipeState) -> PipeState:

        state["pov_id"] = self.pov_id
        state["extrusion_factor_s"] = self.extrusion_factor_s
        state["tolerance_metre"] = self.tolerance_metre
        state["near_far_threshold"] = self.near_far_threshold

        template_paths = prepare_template_paths()

        log_path = Path(__file__).parent / "spatial_calls.log"

        with open(log_path, "w", encoding="utf-8") as log_file:
            relations = execute_spatial_calls(
                state["spatial_plan"],
                state["all_objects"],
                template_paths,
                log_file,
                state["udt_to_ids"],
                state["pov_id"],
                state["extrusion_factor_s"],
                state["tolerance_metre"],
                state["near_far_threshold"]
            )

        state["relations"] = relations
        return state

    def evaluate_rule(self, state: PipeState) -> PipeState:
        evaluation = evaluate_rule(
            state["rule_text"],
            state.get("relations", []),
            self.llm
        )
        state["evaluation"] = evaluation
        return state

    def run_hs_rule_validator(self, rule_text: str) -> Dict[str, Any]:
        if self.chain is None:
            self.build_workflow()
        initial_state: PipeState = {
            "rule_text": rule_text,
            "decomposed_checks": None,
            "all_objects": None,
            "id_to_obj": None,
            "all_ids": None,
            "type_to_ids": None,
            "enriched_checks": None,
            "spatial_plan": None,
            "relations": None,
            "summaries": None,
            "evaluation": None,
        }
        return self.chain.invoke(initial_state)

def main(gold_standard, pov_id=1, extrusion_factor_s=2, tolerance_metre=0.2, near_far_threshold=1):
    # Prepare output directory
    outputs_dir = Path(__file__).parent / "outputs_results"
    outputs_dir.mkdir(exist_ok=True)

    validator = Evaluate_Hs_Rule(pov_id, extrusion_factor_s, tolerance_metre, near_far_threshold)

    # --- Here we initialize final_summary with the desired structure ---
    final_summary: Dict[str, Any] = {"results": {}}

    # To collect per-check times
    exec_times: Dict[str, float] = {}

    # Iterate over each rule and run pipeline
    for rule_id, gs in gold_standard.items():
        start_time = time.perf_counter()  # ⏱️ start

        question       = gs["rule_text"]
        gs_compliant   = gs["overall_compliant"]
        gs_explanation = gs["explanation_summary"]

        print(f"DEBUG: Processing rule '{rule_id}'...'{question}'")
        results = validator.run_hs_rule_validator(question)

        # Filter out large fields
        filtered = {k: v for k, v in results.items()
                    if k not in ("all_objects", "all_ids", "id_to_obj", "type_to_ids", "user_defined_types", "udt_to_ids")}

        # Stop timing
        end_time = time.perf_counter()
        duration = end_time - start_time
        exec_times[rule_id] = duration
        filtered["execution_time_sec"] = duration  # also write in per-rule file

        # Write per-rule file
        rule_file = outputs_dir / f"{rule_id}.json"
        json_str = json.dumps(filtered, ensure_ascii=False, indent=2).replace('\\n', '\n')
        with open(rule_file, "w", encoding="utf-8") as f:
            f.write(json_str)

        # --- Now extract the evaluation and compare to gold standard ---
        eval_dict      = filtered.get("evaluation", {})
        llm_compliant  = eval_dict.get("overall_compliant")
        llm_explanation = eval_dict.get("overall_explanation", "")

        correct = (
            (llm_compliant is True  and gs_compliant is True) or
            (llm_compliant is False and gs_compliant is False)
        )

        # --- Populate final_summary["results"][rule_id] as requested ---
        final_summary["results"][rule_id] = {
            "rule_text":        question,
            "llm_compliant":    llm_compliant,
            "llm_explanation":  llm_explanation,
            "gold_compliant":   gs_compliant,
            "gold_explanation": gs_explanation,
            "correct":          correct,
            "execution_time_sec": duration
        }

    # --- Aggregate execution time stats ---
    total_time = sum(exec_times.values())
    avg_time   = total_time / len(exec_times) if exec_times else 0
    max_rule   = max(exec_times, key=exec_times.get)
    min_rule   = min(exec_times, key=exec_times.get)

    final_summary["execution_time"] = {
        "total_time_sec": total_time,
        "average_time_sec": avg_time,
        "max_time_sec": exec_times[max_rule],
        "max_time_rule": max_rule,
        "min_time_sec": exec_times[min_rule],
        "min_time_rule": min_rule
    }

    # Write consolidated summary
    summary_file = outputs_dir / "final_results.json"
    print(f"DEBUG: Writing consolidated summary to {summary_file}.")
    with open(summary_file, "w", encoding="utf-8") as sf:
        json.dump(final_summary, sf, ensure_ascii=False, indent=2)

    print("Done! Individual rule outputs and final summary written to 'outputs_results'.")

    
if __name__ == "__main__":
    # ————— Define your checks ————— 
    # room2 gold standard D
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

    
    main(gold_standard)