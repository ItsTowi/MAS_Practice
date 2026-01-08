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

        plan = crew_output.pydantic

        # Construcción de un reporte "Super-Informativo"
        md = f"# MISSION PLAN: {plan.plan_name}\n\n"
        
        md += "## Strategic Overview\n"
        md += f"**Approved Targets:** {', '.join(plan.approved_targets)}\n"
        md += f"**Restricted Zones:** {', '.join(plan.no_go_zones) if plan.no_go_zones else 'None identified'}\n\n"
        
        md += "## 🛠️ Tactical Action Sequence\n\n"
        for step in plan.action_sequence:
            md += f"* **{step.unit} in Node {step.node}**: {step.action}. "
            md += f"Rationale: {step.rationale}\n"

        md += "\n## Safety & Emergency Protocols\n"
        for proto in plan.emergency_protocols:
            md += f"- {proto}\n"
        
        md += "\n---\n"
        md += "## Detailed Expert Analysis\n"
        md += plan.markdown_report

        output_path = Path("outputs/master_mission_plan.md")
        output_path.write_text(md, encoding="utf-8")
        
        print(f"✅ Full informative report saved to {output_path}")
        return md

def test_mission():
    flow = MissionTestFlow()
    flow.kickoff()
    print("\nMission Crew process completed successfully")

if __name__ == "__main__":
    test_mission()