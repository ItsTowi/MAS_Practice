import sys
import os
from crewai.flow.flow import Flow, listen, start

#sys.path.append(os.path.abspath("../.."))
from src.mars_exploration.crews.mission_crew.mission_crew import MissionCrew

class MissionTestFlow(Flow):

    @start()
    def load_and_assess(self):
        """
        Unit Test: The Mission Crew performs strategic planning
        """

        print("Starting Mission Crew Test Flow...\n")
        
        inputs = {
            "mission_report_path": "src/inputs/mission_report.md",
            "terrain_data_path": "src/inputs/mars_terrain.graphml"
        }

        output = MissionCrew().crew().kickoff(inputs=inputs)

        if isinstance(output, dict):
            # Si es un dict, intentamos sacar el valor de la respuesta final
            return output.get('final_output', str(output))
        
        return output.raw
    
    @listen(load_and_assess)
    def display_results(self, final_plan):
        print("Strategic Plan Output:\n")
        print(final_plan)

def test_mission():
    try:
        flow = MissionTestFlow()
        flow.kickoff()
    except Exception as e:
        print(f"Error during test_mission: {e}")

if __name__ == "__main__":
    test_mission()