from __future__ import annotations
from typing import Any, Dict

from .contracts import extract_mission_plan_text
from .parse_mission_plan import parse_mission_plan
from .planning import (
    build_orbit_plan,
    build_imaging_plan,
    build_communication_plan,
    build_environment_report,
    export_markdown,
)


def run_satellite_crew(inputs: Dict[str, Any]) -> str:
    """
    Input: mission_plan markdown (text or path).
    Output: Markdown string for Integration Crew.
    Also writes outputs/satellite_plan.md and outputs/satellite_plan.json for your own testing.
    """
    md = extract_mission_plan_text(inputs)
    mission = parse_mission_plan(md)

    plan = {
        "orbit": build_orbit_plan(mission),
        "imaging": build_imaging_plan(mission),
        "communications": build_communication_plan(mission),
        "environment": build_environment_report(mission),
        "notes": ["Derived from MissionCrew mission_plan.md output."],
        "inputs_used": mission,
    }

    md_text = export_markdown(plan)

    # Return the Markdown artifact content (integration can embed it directly)
    return md_text
