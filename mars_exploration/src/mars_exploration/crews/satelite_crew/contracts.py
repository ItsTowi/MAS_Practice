from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from pathlib import Path

def _mars_exploration_root() -> Path:
    # contracts.py is at:
    # mars_exploration/src/mars_exploration/crews/satelite_crew/contracts.py
    # root we want:
    # mars_exploration/
    return Path(__file__).resolve().parents[4]

def extract_mission_plan_text(inputs: Dict[str, Any]) -> str:
    """
    Expected inputs:
      {"mission_plan_md": "<markdown>"} OR
      {"mission_plan_path": "outputs/mission_plan.md"} (relative to mars_exploration/) OR
      {"mission_plan_path": "C:/.../mission_plan.md"} (absolute)
    """
    if not isinstance(inputs, dict):
        return ""

    if "mission_plan_md" in inputs and isinstance(inputs["mission_plan_md"], str):
        return inputs["mission_plan_md"]

    path = inputs.get("mission_plan_path")
    if path is not None:
        p = Path(path)

        # If relative, resolve from mars_exploration/ root
        if not p.is_absolute():
            p = _mars_exploration_root() / p

        return p.read_text(encoding="utf-8")

    if "mission_plan" in inputs and isinstance(inputs["mission_plan"], str):
        return inputs["mission_plan"]

    return ""
