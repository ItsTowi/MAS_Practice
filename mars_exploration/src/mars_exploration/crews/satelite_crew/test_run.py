import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SRC_DIR))

from mars_exploration.crews.satelite_crew.satelite_crew import run_satellite_crew

if __name__ == "__main__":
    # Use mission plan from outputs
    out_md = run_satellite_crew({"mission_plan_path": "outputs/mission_plan.md"})
    print(out_md[:400])
    assert "# Satellite Crew Plan" in out_md
    print("OK")
