import sys
import os
import re
from pathlib import Path
from crewai.flow.flow import Flow, listen, start
from IPython.display import Markdown
from datetime import datetime

#sys.path.append(os.path.abspath("../.."))
from src.mars_exploration.crews.mission_crew.mission_crew import MissionCrew

class MissionTestFlow(Flow):
    """
    Test Flow for Mission Crew
    """

    @start()
    def run_mission_planning(self):
        """
        Unit Test: The Mission Crew performs strategic planning
        """

        print("Starting Mission Crew Test Flow...\n")
        
        inputs = {
            "mission_report_path": "src/mars_exploration/inputs/mission_report.md",
            "terrain_data_path": "src/mars_exploration/inputs/mars_terrain.graphml"
        }

        try:
            result = MissionCrew().crew().kickoff(inputs=inputs)
            return result
        except Exception as e:
            print(f"Error of execution: {e}")
            raise
    
    
    @listen(run_mission_planning)
    def save_markdown_output(self, crew_output):
        print("Strategic Plan Output:\n")

        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        final_text = crew_output.raw
        final_text = re.sub(r"<think>.*?</think>", "", final_text, flags=re.DOTALL).strip() 

        output_path = output_dir / "master_mission_plan.md"
        output_path.write_text(final_text, encoding="utf-8")

        print(f"Master Plan in: {output_path}")
        return final_text

def test_mission():
    flow = MissionTestFlow()
    flow.kickoff()
    print("\nProcesd completed successfully")

if __name__ == "__main__":
    test_mission()