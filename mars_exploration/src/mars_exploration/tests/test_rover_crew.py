import sys
import re
import json
from pathlib import Path
from datetime import datetime

import networkx as nx
from crewai.flow.flow import Flow, listen, start

# Resolve src directory: .../mars_exploration/src
SRC_DIR = Path(__file__).resolve().parents[2]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mars_exploration.crews.rover_crew.rover_crew import RoverCrew


def extract_rover_steps(mission_plan_text: str) -> list[dict]:
    """
    Extract rover-only steps from the mission plan in a future-proof way.
    """
    steps = []
    blocks = re.split(r"\n(?=###\s*Step\s*\d+)", mission_plan_text, flags=re.IGNORECASE)

    for block in blocks:
        m_step = re.search(r"###\s*Step\s*(\d+)", block, flags=re.IGNORECASE)
        if not m_step:
            continue

        step_num = int(m_step.group(1))

        m_unit = re.search(r"\*\*Unit:\*\*\s*([A-Za-z]+)", block, flags=re.IGNORECASE)
        unit = m_unit.group(1).strip().lower() if m_unit else "unknown"
        if unit != "rover":
            continue

        m_target = re.search(r"\*\*Target Node:\*\*\s*(N\d+)", block, flags=re.IGNORECASE)
        target = m_target.group(1).strip() if m_target else "unknown"

        m_task = re.search(r"\*\*Task:\*\*\s*([^\n]+)", block, flags=re.IGNORECASE)
        task = m_task.group(1).strip() if m_task else "unknown"

        steps.append({"step": step_num, "target": target, "task": task})

    return steps


def build_routes_hint(graphml_path: Path, rovers_json_path: Path, rover_steps: list[dict]) -> str:
    """
    Deterministically compute shortest paths and distances.
    """
    g = nx.read_graphml(str(graphml_path))
    rovers = json.loads(rovers_json_path.read_text(encoding="utf-8"))

    targets = sorted({s["target"] for s in rover_steps if s["target"].startswith("N")})
    routes = []

    for rover in rovers:
        rover_id = rover.get("id")
        start = rover.get("location")
        if not rover_id or not start or start not in g.nodes:
            continue

        for target in targets:
            if target not in g.nodes:
                continue

            try:
                path = nx.shortest_path(g, start, target, weight="length")
                dist = nx.shortest_path_length(g, start, target, weight="length")

                energy_cost = 0.0
                has_energy = True
                for a, b in zip(path, path[1:]):
                    e = g.edges[a, b].get("energy")
                    if e is None:
                        has_energy = False
                        break
                    energy_cost += float(e)

                routes.append(
                    {
                        "rover_id": rover_id,
                        "start": start,
                        "target": target,
                        "route": path,
                        "distance": float(dist),
                        "energy_cost": float(energy_cost) if has_energy else None,
                    }
                )
            except Exception:
                continue

    return json.dumps({"routes": routes}, ensure_ascii=False)


class RoverTestFlow(Flow):
    def __init__(self):
        super().__init__()

        # Project root: .../mars_exploration
        self.project_root = SRC_DIR.parent

        # Inputs directory
        self.inputs_dir = SRC_DIR / "mars_exploration" / "inputs"

        # Base outputs directory (shared; mission_plan lives here)
        self.base_outputs_dir = self.project_root / "outputs"
        self.base_outputs_dir.mkdir(parents=True, exist_ok=True)

        # Rover crew outputs directory inside the rover crew package
        self.outputs_dir = (
            SRC_DIR
            / "mars_exploration"
            / "crews"
            / "rover_crew"
            / "outputs"
        )
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    @start()
    def run_rover_planning(self):
        # Read mission plan from root outputs (shared)
        mission_plan_path = self.base_outputs_dir / "mission_plan.md"

        terrain_path = self.inputs_dir / "mars_terrain.graphml"
        rovers_path = self.inputs_dir / "rovers.json"
        mission_report_path = self.inputs_dir / "mission_report.md"  # optional

        required = [mission_plan_path, terrain_path, rovers_path]
        missing = [p for p in required if not p.exists()]
        if missing:
            raise FileNotFoundError(
                "Missing required files:\n" + "\n".join(f"- {p}" for p in missing)
            )

        mission_plan_text = mission_plan_path.read_text(encoding="utf-8")
        rover_steps = extract_rover_steps(mission_plan_text)
        routes_hint = build_routes_hint(terrain_path, rovers_path, rover_steps)

        inputs = {
            "mission_plan": mission_plan_text,
            "terrain_graphml": terrain_path.read_text(encoding="utf-8"),
            "rovers_json": rovers_path.read_text(encoding="utf-8"),
            "routes_hint": routes_hint,
        }

        if mission_report_path.exists():
            inputs["mission_report"] = mission_report_path.read_text(encoding="utf-8")

        return RoverCrew().crew().kickoff(inputs=inputs)

    @listen(run_rover_planning)
    def save_rover_output(self, crew_output):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        text = getattr(crew_output, "raw", str(crew_output))
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

        out_path = self.outputs_dir / f"rover_operation_plan_{ts}.md"
        out_path.write_text(text, encoding="utf-8")
        print(f"Saved rover plan: {out_path}")
        return text


def main():
    RoverTestFlow().kickoff()


if __name__ == "__main__":
    main()
