import sys
import os
from pathlib import Path
from crewai.flow.flow import Flow, listen, start
from datetime import datetime
import json

#sys.path.append(os.path.abspath("../.."))
from src.mars_exploration.crews.mission_crew.mission_crew import MissionCrew

class MissionTestFlow(Flow):
    """
    Test Flow for Mission Crew
    """

    @start()
    def initialize_mission(self):
        """
        Unit Test: The Mission Crew performs strategic planning
        """

        print("Starting Mission Crew Test Flow...\n")
        
        inputs = {
            "mission_report_path": "src/mars_exploration/inputs/mission_report.md",
            "terrain_data_path": "src/mars_exploration/inputs/mars_terrain.graphml"
        }

        #Verify input files
        for key, path in inputs.items():
            if not Path(path).exists():
                raise FileNotFoundError(f"Required input file not found: {path}")
            print(f"Verified: {key}: {path}")

        try:
            result = MissionCrew().crew().kickoff(inputs=inputs)

            # Extract the structured output
            if hasattr(result, 'pydantic'):
                structured_plan = result.pydantic
            elif isinstance(result, dict):
                structured_plan = result
            else:
                structured_plan = result.raw if hasattr(result, 'raw') else str(result)
        
            return {
                "structured_plan": structured_plan,
                "raw_output": result.raw if hasattr(result, 'raw') else str(result),
                "inputs": inputs
            }
        except Exception as e:
            print(f"\nError during Mission Crew execution: {e}")
            raise
    
    
    @listen(initialize_mission)
    def validate_and_save_plan(self, mission_data: dict):
        """
        Validate the geenrated mission plan and save it.
        """
        print("Strategic Plan Output:\n")

        structured_plan = mission_data["structured_plan"]

        validation_passed = True

        print("Running Validation...")

        #1. Strutured plan exists
        if structured_plan is None:
            print("Validation failed: No structured plan generated")
            validation_passed = False
        else:
            print("Structured plan generated")

        # 2. Essential components
        if hasattr(structured_plan, 'scientific_priorities'):
            if len(structured_plan.scientific_priorities) > 0:
                print(f"Scientific prioritied defined ({len(structured_plan.scientific_priorities)} objectives)")
            else:
                print("Warning: No scientific priorities defined")
                validation_passed = False
            
        if hasattr(structured_plan, 'hazard_zones'):
            print(f"Hazard zones identified ({len(structured_plan.hazard_zones)} zones)")
        
        if hasattr(structured_plan, 'resource_allocations'):
            print(f"Resource allocations planned ({len(structured_plan.resource_allocations)} resources)")

        # Save outputs
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        json_path = output_dir / "mission_plan.json"

        try:
            if hasattr(structured_plan, 'model_dump'):
                json_data = structured_plan.model_dump()
            elif hasattr(structured_plan, 'dict'):
                json_data = structured_plan.dict()
            else:
                json_data = mission_data["raw_output"]

            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            print(f"Saved JSON plan: {json_path}")
        except Exception as e:
            print(f"Could not save JSON: {e}")

        md_path = output_dir /"structured_mission_plan.md"
        if md_path.exists():
            print(f"Saved Markdown plan: {md_path}")
            
        print()
        if validation_passed:
            print("Mission Pan validation passed")
        else:
            print("Mission Plan Validation Completed with warnings")

        return mission_data
    
    @listen(validate_and_save_plan)
    def display_summary(self, mission_data: dict):
        """
        Display a human-readable summary of the mission plan.
        """
        print("MISSION PLAN SUMMARY")
        
        structured_plan = mission_data["structured_plan"]
        
        if hasattr(structured_plan, 'mission_summary'):
            print("\nSummary:")
            print(structured_plan.mission_summary)
        
        if hasattr(structured_plan, 'scientific_priorities'):
            print(f"\nScientific Objectives: {len(structured_plan.scientific_priorities)}")
            for i, obj in enumerate(structured_plan.scientific_priorities[:3], 1):
                print(f"   {i}. {obj.name} (Priority: {obj.priority}/10)")
        
        if hasattr(structured_plan, 'hazard_zones'):
            print(f"\nHazard Zones: {len(structured_plan.hazard_zones)}")
            critical_hazards = [h for h in structured_plan.hazard_zones if h.risk_level == "CRITICAL"]
            if critical_hazards:
                print(f"   - {len(critical_hazards)} CRITICAL hazards require immediate attention")
        
        if hasattr(structured_plan, 'restricted_areas'):
            print(f"\nRestricted Areas: {len(structured_plan.restricted_areas)} nodes")
        
        print("Mission Crew execution complete!")

        return mission_data

def test_mission():
    try:
        flow = MissionTestFlow()
        result = flow.kickoff()

        print("\n Mission Planning Flow completed successfully")
        return result
    except Exception as e:
        print(f"Error during test_mission: {e}")

if __name__ == "__main__":
    test_mission()