from __future__ import annotations
import re
from typing import Any, Dict, List


def parse_approved_nodes(md: str) -> List[str]:
    # Matches lines like: "- **Node N90** approved ..."
    pattern = r"- \*\*Node\s+(N\d+)\*\*"
    return re.findall(pattern, md)


def parse_steps(md: str) -> List[Dict[str, Any]]:
    # Extract blocks like:
    # ### Step 1
    # - **Unit:** rover
    # - **Target Node:** N90
    # - **Task:** ...
    # - **Estimated Duration:** 30 minutes
    steps: List[Dict[str, Any]] = []
    step_blocks = re.split(r"\n### Step\s+\d+\n", md)
    # First split chunk is header; ignore
    for block in step_blocks[1:]:
        unit = re.search(r"\*\*Unit:\*\*\s*([a-zA-Z_]+)", block)
        node = re.search(r"\*\*Target Node:\*\*\s*(N\d+)", block)
        task = re.search(r"\*\*Task:\*\*\s*(.+)", block)
        dur = re.search(r"\*\*Estimated Duration:\*\*\s*(.+)", block)

        steps.append({
            "unit": (unit.group(1).strip().lower() if unit else "unknown"),
            "target_node": (node.group(1).strip() if node else "unknown"),
            "task": (task.group(1).strip() if task else ""),
            "duration": (dur.group(1).strip() if dur else ""),
        })
    return steps


def parse_risks(md: str) -> List[str]:
    # Under "##  Identified Mission Risks" bullets
    # Very simple: capture bullet lines after that header until next header
    risks: List[str] = []
    m = re.search(r"##\s*Identified Mission Risks\s*(.*?)(\n##|\Z)", md, re.S)
    if not m:
        return risks
    block = m.group(1)
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            risks.append(line[2:].strip())
    return risks


def parse_mission_plan(md: str) -> Dict[str, Any]:
    return {
        "approved_nodes": parse_approved_nodes(md),
        "steps": parse_steps(md),
        "risks": parse_risks(md),
    }
