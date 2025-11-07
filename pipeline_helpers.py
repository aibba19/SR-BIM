import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from langchain_openai import ChatOpenAI
import os
import yaml
from dotenv import load_dotenv
from db_utils import *
from psycopg2 import sql
from collections import defaultdict

load_dotenv()

def get_openai_llm(model_name="gpt-4o-mini", api_key=None):
    """Get an OpenAI LLM instance."""
    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key or os.getenv("MY_OPENAI_KEY"),
    )

def get_openrouter_llm(model_name="deepseek/deepseek-r1-0528:free"):
    """Get an OpenRouter LLM instance."""
    return ChatOpenAI(
        model=model_name,
        openai_api_key= os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",  # Custom base URL
        #model_kwargs={"max_tokens": max_tokens},
    )

# Default LLM getter that can be modified based on preference
def get_llm(model_name='gpt-4.1-mini-2025-04-14'):
    """Get the default LLM instance."""
    # Change this function to use your preferred LLM

    return get_openai_llm(model_name)

    """Get the default LLM instance via OpenRouter."""
    #return get_openrouter_llm(model_name, max_tokens= 20000)

# Load promtp usin yaml file
def load_prompt_by_name( target_name):
    base_dir = os.path.dirname(_file_)  # directory di utils.py
    file_path = os.path.join(base_dir, "Prompts", "prompts.yaml")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Expecting a list of dicts with 'name' and 'content' keys
    for item in data:
        if item.get('name') == target_name:
            return item.get('content')

def fetch_types_and_names(
    table_name: str = "room_objects",
    id_column: str = "id",
    type_column: str = "ifc_type",
    name_column: str = "name",
    *,
    outfile: Optional[Path | str] = "ifc_types_names.txt",  # set to None to skip writing
    file_mode: str = "w",                                   # or "a" to append
    line_template: str = "{id}  -  {type}  -  {name}\n"     # customise if you like
) -> List[Tuple[int, str, str]]:
    """
    Fetch (id, type, name) tuples from the given table/columns.

    • Prints each tuple.
    • Optionally writes them to *outfile* (text file).
    • Returns the list of tuples [(id, type, name), …].

    Parameters
    ----------
    id_column : str
        Name of the ID column to fetch.
    outfile : str | Path | None
        Where to write the data. Pass None to disable file output.
    file_mode : str
        'w' = overwrite (default), 'a' = append, etc.
    line_template : str
        Format string for each line; supports {id}, {type}, {name}.
    """
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT {id_col}, {type_col}, {name_col} FROM {tbl}").format(
                id_col=sql.Identifier(id_column),
                type_col=sql.Identifier(type_column),
                name_col=sql.Identifier(name_column),
                tbl=sql.Identifier(table_name)
            )
            cur.execute(query)
            rows = cur.fetchall()  # List of (id, type, name)

        # Prepare file output if requested
        writer = None
        if outfile is not None:
            outfile = Path(outfile)
            outfile.parent.mkdir(parents=True, exist_ok=True)
            writer = outfile.open(file_mode, encoding="utf-8")

        # Print and write each row
        for obj_id, obj_type, obj_name in rows:
            line = line_template.format(id=obj_id, type=obj_type, name=obj_name)
            #print(line.rstrip())
            if writer:
                writer.write(line)

        if writer:
            writer.close()

        return rows

    finally:
        conn.close()

def load_objects_and_maps() -> Tuple[List[Tuple[int, str, str]], Dict[int, Tuple[str, str]], List[int], Dict[str, List[int]]]:
    """
    Load all objects from the PostgreSQL DB and build helpful lookup maps.

    Returns
    -------
    all_objects : List of (id, ifc_type, name) tuples
    id_to_obj    : Dict mapping ID → (ifc_type, name)
    all_ids      : List of all object IDs
    type_to_ids  : Dict mapping ifc_type → list of IDs
    """
    print("DEBUG: Fetching all objects (id, type, name) from DB...")
    all_objects = fetch_types_and_names()
    print(f"DEBUG: Retrieved {len(all_objects)} objects.\n")

    # Build id_to_obj mapping: ID → (ifc_type, name)
    id_to_obj: Dict[int, Tuple[str, str]] = {
        obj_id: (ifc_type, name) for obj_id, ifc_type, name in all_objects
    }
    all_ids = list(id_to_obj.keys())

    # Build type_to_ids mapping: ifc_type → [IDs]
    type_to_ids: Dict[str, List[int]] = {}
    for obj_id, ifc_type, _ in all_objects:
        type_to_ids.setdefault(ifc_type, []).append(obj_id)

    print("DEBUG: Built ID→object and type→IDs maps.\n")
    return all_objects, id_to_obj, all_ids, type_to_ids


def execute_spatial_calls(
    plan: Dict,
    all_objects: List[Tuple[int, str, str]],
    template_paths: Dict[str, Path],
    log_file,
    udt_to_ids: Dict[str, List[int]],
    pov_id: int,
    extrusion_factor_s: int,
    tolerance_metre: float,
    near_far_threshold: float,

) -> List[Dict]:
    """
    Execute spatial calls (SQL templates) for each entry in the plan,
    using a provided udt_to_ids map to expand any IFC-type UDTs into real object IDs.

    Args:
      plan: the spatial_plan dict (with plans[*].reference_ifc_types / against_ifc_types)
      all_objects: list of tuples (id, ifc_type, name)
      template_paths: mapping from template name to .sql Path
      log_file: open file handle for debugging
      udt_to_ids: dict mapping each UDT string → list of matching object IDs

    Returns:
      A list of result dicts for those object pairs that expose a violation
      (i.e. held == use_positive).
    """

    # Build quick lookup from ID to (type,name)
    id_to_obj = {oid: (ifc, name) for oid, ifc, name in all_objects}
    all_ids = [obj_id for obj_id, _, _ in all_objects]

    conn = get_connection()
    results: List[Dict] = []

    for entry in plan.get("plans", []):
        idx          = entry["check_index"]
        use_positive = entry.get("use_positive", True)
        print(f"DEBUG: check_index={idx}, use_positive={use_positive}")

        for tmpl in entry["templates"]:
            tpl_name = tmpl["template"]
            a_src, b_src = tmpl["a_source"], tmpl["b_source"]

            
            # Expand reference IDs
            if a_src == "reference_ifc_types":
                # flatten the lists of IDs for each UDT
                a_ids = [
                    oid
                    for udt in entry["reference"].get("reference_ifc_types", [])
                    for oid in udt_to_ids.get(udt, [])
                ]
            else:  # any_nearby or reference_ids
                # if they provided explicit reference_ids, use them; otherwise all IDs
                a_ids = entry["reference"].get("reference_ids", list(id_to_obj))

            # Expand against IDs
            if b_src == "against_ifc_types":
                b_ids = [
                    oid
                    for udt in entry["against"].get("against_ifc_types", [])
                    for oid in udt_to_ids.get(udt, [])
                ]
            else:  # any_nearby or against_ids
                b_ids = (
                    entry["against"].get("against_ids", list(id_to_obj))
                    if b_src == "against_ids"
                    else list(id_to_obj)
                )
            

            for a_id in a_ids:
                a_type, a_name = id_to_obj[a_id]
                for b_id in b_ids:
                    if a_id == b_id:
                        continue
                    b_type, b_name = id_to_obj[b_id]

                    call = {
                        "type":     "template",
                        "template": tpl_name,
                        "a_id":     a_id,
                        "b_id":     b_id
                    }

                    # --- log the call ---
                    log_file.write("=== SPATIAL CALL ===\n")
                    log_file.write(json.dumps(call, ensure_ascii=False) + "\n")

                    resp = run_spatial_call(conn, call, template_paths, pov_id, extrusion_factor_s, tolerance_metre, near_far_threshold)

                    # --- log the result ---
                    log_file.write("RESULT:\n")
                    log_file.write(json.dumps(resp, ensure_ascii=False) + "\n\n")
                    log_file.flush()

                    # --- interpret held vs. not-held ---
                    held = False
                    relation_value = None
                    rows = resp.get("rows", [])
                    if rows:
                        first = rows[0]
                        if tpl_name == "touches":
                            held = bool(first[0])
                            relation_value = first[1]
                        elif tpl_name in {"front", "left", "right", "behind", "above", "below"}:
                            held = bool(first[3])
                            if held:
                                relation_value = first[4]
                        elif tpl_name in {"near", "far"}:
                            is_near = bool(first[2])
                            is_far  = bool(first[3])
                            held = is_near if tpl_name == "near" else is_far
                            if held:
                                relation_value = first[0]
                        elif tpl_name == "contains":
                            # first = rows[0] = (is contained flag, float percentage contained x in y , phrase explaining relation)
                            is_contained = bool(first[0])
                            held = is_contained
                            if held:
                                relation_value = first[2]

                        else:
                            # composed relations should return (flag, text)
                            held = bool(first[0])
                            if len(first) > 1:
                                relation_value = first[1]

                    # save only matches that expose a violation
                    if held == use_positive:
                        results.append({
                            "check_index":    idx,
                            "template":       tpl_name,
                            "a_id":           a_id,
                            "a_name":         a_name,
                            "a_type":         a_type,
                            "b_id":           b_id,
                            "b_name":         b_name,
                            "b_type":         b_type,
                            "relation_value": relation_value
                        })

    print(f"DEBUG: Collected {len(results)} results matching use_positive.\n")
    return results

def extract_user_defined_types(
    elements: List[Tuple[int, str, str]]
) -> List[str]:
    """
    Extracts and returns a list of unique user-defined types from a list of IFC elements.
    Also writes each user-defined type to a file named 'user_defined_type' inside the 'outputs_results' folder.

    Args:
        elements: list of tuples (index, ifc_type, instance_str), where
            - index (int): numeric identifier
            - ifc_type (str): IFC type (e.g., "IfcDoor")
            - instance_str (str): string in the format "prefix[:display][:id]"

    Returns:
        List[str]: list of unique user-defined types, formatted as
                   "IfcType_prefix" or "IfcType_prefix_display"
    """
    udts = []
    for idx, ifc_type, inst_str in elements:
        segs = inst_str.split(':')
        if len(segs) == 3:
            prefix, display, _ = segs
        elif len(segs) == 2:
            prefix, _ = segs
            display = ""
        else:
            prefix = segs[0]
            display = ""
        
        prefix = prefix.strip()
        display = display.strip()
        combined = f"{prefix}_{display}" if display else prefix
        udt = f"{ifc_type.strip()}_{combined}"
        
        if udt not in udts:
            udts.append(udt)
    
    # Ensure output directory exists
    os.makedirs('outputs_results', exist_ok=True)
    # Write each user-defined type to file
    file_path = os.path.join('outputs_results', 'user_defined_type')
    with open(file_path, 'w', encoding='utf-8') as f:
        for udt in udts:
            f.write(f"{udt}\n")
    
    return udts



def ids_from_udts(
    udts: List[str],
    all_objects: List[Tuple[int, str, str]]
) -> Dict[str, List[int]]:
    """
    For each user‐defined type (UDT), return the list of object IDs whose
    IFC type and name match.  A UDT is formatted like:
       "<IfcType>_<name segments joined by '_'>"
    whereas real object names use ':' to separate the last ID.
    We normalize real names by replacing ':' with '_', then require that
    all segments of the UDT after the first '_' appear in that normalized name.

    Args:
      udts:        list of user‐defined types, e.g.
                   "IfcBuildingElementProxy_Fire_Safety-..._EX-3002"
      all_objects: list of tuples (id, ifc_type, name), where name is
                   the DB string with colons, e.g.
                   "Fire_Safety-...:EX-3002:323036"

    Returns:
      A dict mapping each UDT → list of matching object IDs.
    """
    mapping: Dict[str, List[int]] = {}
    # Pre‐normalize all object names once
    normalized = {
        oid: o_name.replace(":", "_")
        for oid, _, o_name in all_objects
    }

    for udt in udts:
        # if the UDT is literally "any", treat as wildcard → all IDs
        if udt.lower() == "any":
            mapping[udt] = [oid for oid, _, _ in all_objects]
            continue

        # Split off the ifc_type from the rest
        if "_" not in udt:
            mapping[udt] = []
            continue
        ifc_type, key = udt.split("_", 1)
        # Break the key into segments that must all appear in the normalized name
        segments = [seg for seg in key.split("_") if seg]

        matched_ids: List[int] = []
        for oid, o_ifc, _ in all_objects:
            if o_ifc != ifc_type:
                continue
            norm_name = normalized[oid]
            # require all pieces to appear
            if all(seg in norm_name for seg in segments):
                matched_ids.append(oid)

        mapping[udt] = matched_ids

    return mapping


def summarize_plan_results_to_list(
    spatial_plan: Dict[str, Any],
    results: List[Dict[str, Any]],
    udt_to_ids: Optional[Dict[str, List[int]]],
    id_to_obj: Dict[int, Tuple[str, str]]
) -> List[str]:
    """
    Produce compact, multi-line summaries grouped by plan and reference object.
    - One block per plan, with a header.
    - Under each header, one subsection per reference ID, listing each tested template
      and its targets (or 'none').
    - Special cases:
      • 'contains': raw relation_value(s).
      • 'on_top_of': parse relation_value to extract X/Y IDs and lookup names.
    """
    # Build plan map
    plan_map = {e["check_index"]: e for e in spatial_plan.get("plans", [])}

    # Index results by (check_index, a_id, template)
    idx: Dict[Tuple[int,int,str], List[Dict[str,Any]]] = defaultdict(list)
    for r in results:
        idx[(r["check_index"], r["a_id"], r["template"])].append(r)

    summaries: List[str] = []

    for chk, plan in plan_map.items():
        # 1) Header
        rels = [t["template"] for t in plan["templates"]]
        rels_str = ", ".join(rels)
        rt = plan.get("relation_text", "")
        against = plan["against"]
        if against["type"] == "any":
            against_desc = "any object instances"
        else:
            ag = against.get("against_ifc_types", [])
            against_desc = ", ".join(ag) + " instances"

        header = f"Plan {chk} (\"{rt}\"): tested [{rels_str}] against {against_desc}"

        # 2) Reference IDs
        if plan["reference"]["type"] == "any" or udt_to_ids is None:
            a_ids = {r["a_id"] for r in results if r["check_index"] == chk}
        else:
            a_ids = set()
            for udt in plan["reference"]["reference_ifc_types"]:
                a_ids.update(udt_to_ids.get(udt, []))

        # 3) Build lines for this plan
        lines = [header]
        for a_id in sorted(a_ids):
            a_name = id_to_obj[a_id][1]
            lines.append(f"  • {a_name} (ID:{a_id}):")
            for tpl in rels:
                recs = idx.get((chk, a_id, tpl), [])

                # contains: raw
                if tpl == "contains":
                    if recs:
                        for r in recs:
                            lines.append(f"      – contains: {r['relation_value']}")
                    else:
                        lines.append(f"      – contains: none")
                    continue

                # on_top_of: parse IDs and lookup names
                if tpl == "on_top_of":
                    if recs:
                        for r in recs:
                            rv = r["relation_value"]
                            ids = re.findall(r"ID[:=] *(\d+)", rv)
                            if len(ids) >= 2:
                                x, y = map(int, ids[:2])
                                xn = id_to_obj[x][1]
                                yn = id_to_obj[y][1]
                                lines.append(
                                    f"      – on_top_of: {xn} (ID:{x}) is on top of {yn} (ID:{y})"
                                )
                            else:
                                lines.append(f"      – on_top_of: {rv}")
                    else:
                        lines.append(f"      – on_top_of: none")
                    continue

                # other templates
                if recs:
                    targets = [
                        f"{r['b_name']} (ID:{r['b_id']})"
                        for r in recs
                    ]
                    part = ", ".join(targets)
                else:
                    part = "No relation with " + against_desc

                # above and below: add "is" expliciting relation way 
                if tpl in ["above", "below"]:
                    lines.append(f"      – Is {tpl}: {part}")
                else:
                    lines.append(f"      – {tpl}: {part}")

        # 4) append one block
        summaries.append("\n".join(lines))

    return summaries





