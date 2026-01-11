#!/usr/bin/env python
import os
from pathlib import Path
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router, and_

from mars_exploration.crews.mission_crew.mission_crew import MissionCrew
from mars_exploration.crews.rover_crew.rover_crew import RoverCrew
from mars_exploration.crews.drone_crew.drone_crew import DroneCrew
from mars_exploration.crews.integration_crew.integration_crew import IntegrationCrew
from mars_exploration.crews.satelite_crew.satelite_crew import SatelliteCrew

# Utils
from mars_exploration.tests.test_rover_crew import extract_rover_steps, build_routes_hint
from mars_exploration.utils.utils_markdown import mission_crew_markdown


class MarsExplorationState(BaseModel):
    # Inicializamos con valores por defecto para evitar que Path("") apunte al directorio actual
    mission_plan_text: str = ""
    mission_plan_path: str = "outputs/mission_plan.md"
    rover_report_path: str = "outputs/rover_operation_plan"
    drone_report_path: str = "outputs/drone_report.md"
    satellite_report_path: str = "outputs/satelite_plan.md"
    final_report_path: str = "outputs/final_mission.md"

class MarsExplorationFlow(Flow[MarsExplorationState]):

    @start()
    def strategic_assessment(self):
        Path("outputs").mkdir(exist_ok=True)
        
        plan_path = Path(self.state.mission_plan_path)
        
        print("Mission Crew Running")

        inputs = {
            "mission_report_path": "src/mars_exploration/inputs/mission_report.md",
            "terrain_data_path": "src/mars_exploration/inputs/mars_terrain.graphml"
        }

        result = MissionCrew().crew().kickoff(inputs=inputs)

        mission_crew_markdown(crew_output=result)

        self.state.mission_plan_path = "outputs/mission_plan.md"
        return result

    @listen("strategic_assessment")
    def run_rover_mission(self, mission_output):
        
        print("Rover Crew Running")

        terrain_path = Path("src/mars_exploration/inputs/mars_terrain.graphml")
        rovers_path = Path("src/mars_exploration/inputs/rovers.json")

        mission_plan_text = Path(self.state.mission_plan_path).read_text(encoding="utf-8")

        rover_steps = extract_rover_steps(mission_plan_text)
        routes_hint = build_routes_hint(terrain_path, rovers_path, rover_steps)
        
        rover_inputs = {
            "mission_plan": mission_plan_text,
            "terrain_graphml": terrain_path.read_text(encoding="utf-8"),
            "rovers_json": rovers_path.read_text(encoding="utf-8"),
            "routes_hint": routes_hint
        }

        result = RoverCrew().crew().kickoff(inputs=rover_inputs)
        
        Path(self.state.rover_report_path).write_text(result.raw, encoding="utf-8")
        return result
        
    @listen("strategic_assessment")
    def run_drone_mission(self, mission_output):
        print("Drone Crew")

        drone_inputs = {
            "mission_report": self.state.mission_plan_text
        }

        result = DroneCrew().crew().kickoff(inputs=drone_inputs)
        report_path = Path(self.state.drone_report_path)


        output_content = result.raw if hasattr(result, 'raw') else str(result)

        report_path.write_text(output_content, encoding="utf-8")

        # Path(self.state.drone_report_path).write_text(result.raw, encoding="utf-8")
        return result
   
    
    @listen("strategic_assessment")
    def run_satellite_mission(self, mission_output):
        print("Satellite Crew Running")

        mission_plan_text = Path(self.state.mission_plan_path).read_text(encoding="utf-8")

        satellite_inputs = {
            "mission_plan_md": mission_plan_text
        }

        result = SatelliteCrew().crew().kickoff(inputs=satellite_inputs)

        satellite_report_path = "mars_exploration/outputs/satellite_plan.md"
        
        Path(satellite_report_path).write_text(result.raw, encoding="utf-8")
        self.state.satellite_report_path = satellite_report_path

        return result


    @listen(and_(run_rover_mission, run_drone_mission, run_satellite_mission))
    def finalize_integration(self, results):
        print("Integration Crew")

        integration_inputs = {
            "rover_report": Path(self.state.rover_report_path).read_text(encoding="utf-8"),
            "drone_report": Path(self.state.drone_report_path).read_text(encoding="utf-8"),
            "satellite_report": Path(self.state.satellite_report_path).read_text(encoding="utf-8"),
            "mission_goals": "Consolidate all surface and aerial data into a unified mission log."
        }

        final_result = IntegrationCrew().crew().kickoff(inputs=integration_inputs)

        output_content = final_result.raw if hasattr(final_result, 'raw') else str(final_result)
        report_path = Path(self.state.final_report_path)

        report_path.write_text(output_content, encoding="utf-8")

        return final_result
    
def run():
    try:
        flow = MarsExplorationFlow()
        flow.kickoff()
    except Exception as e:
        print(f"❌ Error en el Flow: {e}")

if __name__ == "__main__":
    run()



