#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from crewai.flow.flow import Flow, listen, start, router

# Importing the 5 required crews based on your MAS design
from mars_exploration.crews.mission_crew import MissionCrew
from mars_exploration.crews.rover_crew import RoverCrew
from mars_exploration.crews.drone_crew import DroneCrew
from mars_exploration.crews.satelite_crew import SatelliteCrew
from mars_exploration.crews.integration_crew import IntegrationCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

class MarsExplorationFlow(Flow):
    
    """
    Implementation of the coordination and implementation preliminary revision.
    This flow manages the lifecycle of the Mars exploration mission.
    """
    
    @start()
    def strategic_assessment(self):
        """
        Step 1: The Mission Crew performs strategic planning and hazard assessment.
        """
        print("--- [Flow] Starting Strategic Planning (Mission Crew) ---")
        # In a real execution, 'inputs' would include the mission report
        # The Hazard Assessment Agent determines the 'hazard_score'
        output = MissionCrew().crew().kickoff()
        return output
    
    
    ### ROUTER WHAT?

    @listen("standard_exploration")
    def run_surface_mission(self, assessment_data):
        """
        Scenario A: Normal conditions. Drone and Rover crews coordinate for surface work.
        """
        print("--- [Flow] Executing Surface Mission (Rover & Drone Crews) ---")
        # Coordination: Rover and Drone crews run asynchronously to maximize efficiency
        rover_task = RoverCrew().crew().kickoff_async(inputs=assessment_data)
        drone_task = DroneCrew().crew().kickoff_async(inputs=assessment_data)
       
        return {"rover": rover_task, "drone": drone_task}

    @listen("orbital_priority")
    def run_satellite_mission(self, assessment_data):
        """
        Scenario B: Dangerous surface conditions. Focus exclusively on orbital data.
        """
        print("--- [Flow] Executing Orbital Mission (Satellite Crew) ---")
        return SatelliteCrew().crew().kickoff(inputs=assessment_data)

    @listen(["run_surface_mission", "run_satellite_mission"])
    def finalize_integration(self, mission_results):
        """
        Step 3: Integration Crew fuses data and resolves anomalies for the final report.
        """
        print("--- [Flow] Finalizing Integration (Integration Crew) ---")
        # The Data Fusioner and Anomaly Detector agents process all gathered data
        final_report = IntegrationCrew().crew().kickoff(inputs={"results": mission_results})
        return final_report

def run():
    """Run the Mars Exploration Flow."""
    try:
        flow = MarsExplorationFlow()
        flow.kickoff()
    except Exception as e:
        raise Exception(f"An error occurred while running the flow: {e}")

def train():
    """Train the flow's internal crews for optimized coordination."""
    try:
        # Lab 07 training logic applied to the flow context
        flow = MarsExplorationFlow()
        flow.train(n_iterations=int(sys.argv[1]), filename=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while training the flow: {e}")

if __name__ == "__main__":
    run()
