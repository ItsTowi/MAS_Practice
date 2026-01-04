import sys
from pathlib import Path

# This file is in: .../mars_exploration/src/mars_exploration/crews/satelite_crew/test_run.py
# We want to add: .../mars_exploration/src  to sys.path
SRC_DIR = Path(__file__).resolve().parents[3]  # points to .../mars_exploration/src
sys.path.insert(0, str(SRC_DIR))

from mars_exploration.crews.satelite_crew.contracts import STAND_IN_MISSION_CONTEXT
from mars_exploration.crews.satelite_crew.satelite_crew import run_satellite_crew

if __name__ == "__main__":
    out = run_satellite_crew(STAND_IN_MISSION_CONTEXT)
    print(out["crew"])
    print(out["artifacts"])
