from __future__ import annotations
from typing import Any, Dict, List
from pathlib import Path
import json

from .contracts import extract_mission_context, satellite_output_contract


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def build_orbit_plan(ctx: Dict[str, Any]) -> Dict[str, Any]:
    hazards = ctx.get("hazards", {})
    dust = hazards.get("dust_storm", {})
    level = (dust.get("level") or "low").lower()

    adjustments: List[Dict[str, Any]] = []
    # Placeholder logic: in real version you'll use satellites.json + mission targets
    if level in ("high", "critical"):
        adjustments.append({
            "satellite_id": "SAT-1",
            "change_type": "prioritize_comms",
            "rationale": "High dust storm: imaging quality reduced, prioritize comm relay and wide-area monitoring."
        })
    else:
        adjustments.append({
            "satellite_id": "SAT-1",
            "change_type": "retask_imaging",
            "rationale": "No severe dust storm: proceed with planned high-resolution imaging for priority regions."
        })

    return {
        "adjustments": adjustments,
        "coverage_notes": ["Placeholder coverage assumptions (Task 2/early Task 3)."],
        "constraints": [],
    }


def build_imaging_plan(ctx: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal imaging requests derived from objectives/priorities
    objectives = ctx.get("objectives", [])
    priorities = ctx.get("priorities", {})

    requests: List[Dict[str, Any]] = []
    # Keep it simple: 3 requests with stable fields
    requests.append({
        "target_id": "IMG-001",
        "node_or_region": "region_A",
        "reason": "High-priority mapping for terrain assessment and scientific context.",
        "priority": 1,
    })
    requests.append({
        "target_id": "IMG-002",
        "node_or_region": "region_B",
        "reason": "Support rover/drone planning with updated surface imagery.",
        "priority": 2,
    })
    requests.append({
        "target_id": "IMG-003",
        "node_or_region": "region_C",
        "reason": "Monitor hazards evolution (e.g., dust storm boundaries).",
        "priority": 2,
    })

    return {
        "requests": requests,
        "assumptions": [
            "Targets are placeholders until Mission Crew provides explicit target nodes/regions."
        ],
        "notes": [
            f"Derived from objectives={len(objectives)} and priorities keys={list(priorities.keys())}."
        ],
    }


def build_communication_plan(ctx: Dict[str, Any]) -> Dict[str, Any]:
    constraints = ctx.get("constraints", {})
    min_windows = int(constraints.get("min_comm_windows", 3) or 3)

    windows: List[Dict[str, Any]] = []
    # Placeholder windows - Integration crew can render this regardless of exact times
    for i in range(min_windows):
        windows.append({
            "window_id": f"COM-{i+1:03d}",
            "start": f"SOL+{i} 10:00",
            "end": f"SOL+{i} 10:15",
            "link": "satellite->earth",
        })

    # Add at least one relay example
    windows.append({
        "window_id": "COM-RELAY-001",
        "start": "SOL+0 12:00",
        "end": "SOL+0 12:10",
        "link": "satellite->asset:generic",
    })

    return {
        "windows": windows,
        "bandwidth_notes": [
            f"max_downlink_per_sol={constraints.get('max_downlink_per_sol', 'unknown')}"
        ],
        "contingency": [
            "If a comm window is missed, queue high-priority science packets for the next available window."
        ],
    }


def build_environment_report(ctx: Dict[str, Any]) -> Dict[str, Any]:
    hazards = ctx.get("hazards", {})

    hazard_list: List[Dict[str, Any]] = []
    for hazard_type, info in hazards.items():
        level = (info.get("level") or "low").lower()
        area = info.get("area") or "unknown"
        # Dummy confidence rule
        confidence = 0.7 if level in ("medium", "high", "critical") else 0.5

        recommended = "Continue nominal ops"
        if level in ("high", "critical"):
            recommended = "Increase monitoring and prioritize comm relay; reduce high-res imaging if visibility is low."

        hazard_list.append({
            "hazard_type": hazard_type,
            "severity": level if level in ("low", "medium", "high", "critical") else "low",
            "affected_area": area,
            "confidence": confidence,
            "recommended_action": recommended,
        })

    summary = "Environmental hazards summarized from mission context (placeholder until orbital sensors are integrated)."
    return {"hazards": hazard_list, "summary": summary}


def export_artifacts(plan: Dict[str, Any]) -> Dict[str, str]:
    """
    Writes JSON + MD artifacts for easy demo/testing.
    Returns artifact paths to include in Integration Crew input.
    """
    json_path = OUTPUT_DIR / "satellite_plan.json"
    md_path = OUTPUT_DIR / "satellite_plan.md"

    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    md_lines: List[str] = []
    md_lines.append("# Satellite Crew Plan\n\n")

    md_lines.append("## Orbit\n")
    for adj in plan["orbit"]["adjustments"]:
        md_lines.append(f"- **{adj['satellite_id']}**: {adj['change_type']} — {adj['rationale']}\n")

    md_lines.append("\n## Imaging\n")
    for r in plan["imaging"]["requests"]:
        md_lines.append(f"- (P{r['priority']}) **{r['target_id']}** @ {r['node_or_region']}: {r['reason']}\n")

    md_lines.append("\n## Communications\n")
    for w in plan["communications"]["windows"]:
        md_lines.append(f"- **{w['window_id']}** {w['start']} → {w['end']} ({w['link']})\n")

    md_lines.append("\n## Environment / Hazards\n")
    md_lines.append(plan["environment"]["summary"] + "\n")
    for h in plan["environment"]["hazards"]:
        md_lines.append(
            f"- **{h['hazard_type']}** ({h['severity']}) in {h['affected_area']}, conf={h['confidence']}: {h['recommended_action']}\n"
        )

    md_path.write_text("".join(md_lines), encoding="utf-8")

    return {"json": str(json_path), "md": str(md_path)}


def run_satellite_crew(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point that other crews/Flow can call.
    - Reads mission context (from Mission Crew output or stand-in)
    - Produces a satellite plan
    - Returns a stable output contract for Integration Crew
    """
    ctx = extract_mission_context(inputs)

    plan = {
        "orbit": build_orbit_plan(ctx),
        "imaging": build_imaging_plan(ctx),
        "communications": build_communication_plan(ctx),
        "environment": build_environment_report(ctx),
        "notes": [
            "This is a preliminary Satellite Crew implementation designed to be compatible with Mission and Integration crews."
        ],
        "inputs_used": ctx,
    }

    artifacts = export_artifacts(plan)
    return satellite_output_contract(plan=plan, artifacts=artifacts)
