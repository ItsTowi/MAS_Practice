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
    @start()
    def strategic_assessment(self):
        """
        Step 1: The Mission Crew performs strategic planning and hazard assessment.
        """
        print("--- [Flow] Starting Strategic Planning (Mission Crew) ---")
        output = MissionCrew().crew().kickoff()
        return output
    
    ### ROUTER WHAT?

    @listen("rover_exploration")
    def run_rover_mission(self, assessment_data):
        print("--- [Flow] Executing Surface Mission (Rover & Drone Crews) ---")
        # Coordination: Rover and Drone crews run asynchronously to maximize efficiency
        rover_task = RoverCrew().crew().kickoff_async(inputs=assessment_data)
       
        return ({"rover": rover_task})

    @listen("satelite_exploration")
    def run_satellite_mission(self, assessment_data):
        print("--- [Flow] Executing Orbital Mission (Satellite Crew) ---")
        return SatelliteCrew().crew().kickoff(inputs=assessment_data)
    
    @listen("drone_exploration")
    def run_drone_mission(self, assessment_data):
        drone_task = DroneCrew().crew().kickoff_async(inputs=assessment_data)
        return  ({"drone": drone_task})

    #and
    @listen(["run_rover_mission", "run_satellite_mission", "run_drone_mission"])
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
