from __future__ import annotations
from typing import Any, Dict, List, Tuple


def extract_mission_context(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts either:
      A) inputs = {"mission_context": {...}}
      B) inputs = {...}  (mission_context already flattened)
    Returns a normalized context with stable keys and safe defaults.
    """
    ctx = inputs.get("mission_context", inputs) if isinstance(inputs, dict) else {}

    objectives = ctx.get("objectives", []) or []
    priorities = ctx.get("priorities", {}) or {}
    constraints = ctx.get("constraints", {}) or {}
    hazards = ctx.get("hazards", {}) or {}

    return {
        "objectives": objectives,
        "priorities": priorities,
        "constraints": constraints,
        "hazards": hazards,
    }


def satellite_output_contract(plan: Dict[str, Any], artifacts: Dict[str, str] | None = None) -> Dict[str, Any]:
    """
    Standard output for Integration Crew consumption.
    """
    return {
        "crew": "satellite",
        "plan": plan,
        "artifacts": artifacts or {},
    }


# A stand-in you can use while Mission Crew isn't implemented yet.
STAND_IN_MISSION_CONTEXT: Dict[str, Any] = {
    "mission_context": {
        "objectives": [
            "Provide high-resolution imaging for priority regions",
            "Ensure daily data downlink to Earth when possible",
        ],
        "priorities": {
            "P1": ["comms", "hazard_monitoring"],
            "P2": ["imaging_targets"],
        },
        "constraints": {
            "max_downlink_per_sol": "2GB",
            "min_comm_windows": 3,
        },
        "hazards": {
            "dust_storm": {"level": "medium", "area": "sector_C"},
            "radiation": {"level": "low", "area": "global"},
        },
    }
}


