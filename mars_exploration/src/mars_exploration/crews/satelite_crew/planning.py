from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from pathlib import Path

def _mars_exploration_root() -> Path:
    return Path(__file__).resolve().parents[4]

OUTPUT_DIR = _mars_exploration_root() / "outputs"


def build_orbit_plan(mission: Dict[str, Any]) -> Dict[str, Any]:
    # Deterministic placeholder: could later use satellites.json
    return {
        "adjustments": [
            {
                "satellite_id": "SAT-1",
                "change_type": "coverage_schedule",
                "rationale": "Cover approved target nodes and align imaging with planned action sequence.",
            }
        ],
        "coverage_notes": [
            f"Approved nodes count: {len(mission.get('approved_nodes', []))}",
            "Orbit plan is a placeholder schedule (can be refined with real orbital mechanics later).",
        ],
        "constraints": [],
    }


def build_imaging_plan(mission: Dict[str, Any]) -> Dict[str, Any]:
    nodes = mission.get("approved_nodes", [])
    requests: List[Dict[str, Any]] = []

    # Prioritize first 3-6 approved nodes for imaging
    for i, node in enumerate(nodes[:6], start=1):
        requests.append({
            "target_id": f"IMG-{i:03d}",
            "node_or_region": node,
            "reason": "High-resolution imaging for scientific operations support.",
            "priority": 1 if i <= 3 else 2,
        })

    if not requests:
        # fallback
        requests.append({
            "target_id": "IMG-001",
            "node_or_region": "unknown",
            "reason": "No approved nodes found in mission_plan.md; imaging plan uses placeholder target.",
            "priority": 3,
        })

    return {
        "requests": requests,
        "assumptions": [
            "Imaging requests derived from 'Approved Target Nodes' in mission_plan.md."
        ],
        "notes": [],
    }


def build_communication_plan(mission: Dict[str, Any]) -> Dict[str, Any]:
    steps = mission.get("steps", [])
    windows: List[Dict[str, Any]] = []

    # 1) Earth downlink windows (at least 2)
    windows.append({
        "window_id": "COM-EARTH-001",
        "start": "SOL+0 09:00",
        "end": "SOL+0 09:15",
        "link": "satellite->earth",
    })
    windows.append({
        "window_id": "COM-EARTH-002",
        "start": "SOL+0 18:00",
        "end": "SOL+0 18:15",
        "link": "satellite->earth",
    })

    # 2) Relay windows based on planned steps (generic asset ids)
    for idx, s in enumerate(steps[:5], start=1):
        unit = s.get("unit", "asset")
        node = s.get("target_node", "unknown")
        windows.append({
            "window_id": f"COM-RELAY-{idx:03d}",
            "start": f"SOL+0 {10+idx:02d}:00",
            "end": f"SOL+0 {10+idx:02d}:10",
            "link": f"satellite->{unit}:{node}",
        })

    return {
        "windows": windows,
        "bandwidth_notes": ["Placeholder windows; can be tied to real satellite comm windows later."],
        "contingency": ["If a relay window is missed, queue high-priority science data for the next downlink."],
    }


def build_environment_report(mission: Dict[str, Any]) -> Dict[str, Any]:
    risks = mission.get("risks", [])
    hazards: List[Dict[str, Any]] = []

    # Minimal mapping: infer hazards from risk text
    for r in risks:
        r_low = r.lower()
        if "dust" in r_low:
            hazards.append({
                "hazard_type": "dust_storm",
                "severity": "high",
                "affected_area": "unknown",
                "confidence": 0.6,
                "recommended_action": "Prioritize comm relay and monitoring; reduce high-res imaging if visibility drops.",
            })
        elif "energy" in r_low:
            hazards.append({
                "hazard_type": "energy_risk",
                "severity": "high",
                "affected_area": "node-specific",
                "confidence": 0.7,
                "recommended_action": "Prioritize near-term downlink of critical data; coordinate with rover scheduling.",
            })
        elif "time limit" in r_low or "time" in r_low:
            hazards.append({
                "hazard_type": "schedule_risk",
                "severity": "medium",
                "affected_area": "node-specific",
                "confidence": 0.6,
                "recommended_action": "Consider reducing imaging workload and focus on comm windows for progress updates.",
            })

    summary = "Environment and operational risks inferred from 'Identified Mission Risks' section."
    return {"hazards": hazards, "summary": summary}


def export_markdown(plan: Dict[str, Any]) -> str:
    """
    Writes ONLY Markdown to mars_exploration/outputs/satellite_plan.md
    Returns the markdown text (also useful to return to Integration Crew).
    """
    md_path = OUTPUT_DIR / "satellite_plan.md"

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

    md_lines.append("\n## Environment / Risks\n")
    md_lines.append(plan["environment"]["summary"] + "\n")
    for h in plan["environment"]["hazards"]:
        md_lines.append(
            f"- **{h['hazard_type']}** ({h['severity']}) area={h['affected_area']} conf={h['confidence']}: {h['recommended_action']}\n"
        )

    md_text = "".join(md_lines)
    md_path.write_text(md_text, encoding="utf-8")
    return md_text
