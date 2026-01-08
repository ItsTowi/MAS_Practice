import sys
import os
import re
from pathlib import Path
from crewai.flow.flow import Flow, listen, start
from IPython.display import Markdown
from datetime import datetime

#sys.path.append(os.path.abspath("../.."))
from mars_exploration.crews.mission_crew.mission_crew import MissionCrew

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

        md = []

        md.append("# 🛰️ Mars Exploration Mission Plan\n")
        md.append(f"**Mission ID:** `{plan.mission_id}`")
        md.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
        md.append("---\n")

        # Approved Nodes
        md.append("## ✅ Approved Target Nodes\n")
        for node in plan.approved_nodes:
            md.append(f"- **Node {node}** approved for scientific operations.")
        md.append("\n---\n")

        # Action Sequence
        md.append("## 🧭 Planned Action Sequence\n")

        for action in plan.actions:
            md.append(
                f"### Step {action.step}\n"
                f"- **Unit:** {action.unit}\n"
                f"- **Target Node:** {action.node}\n"
                f"- **Task:** {action.task}\n"
                f"- **Estimated Duration:** {action.duration_min} minutes\n"
            )

        md.append("\n---\n")

        # Risks
        md.append("## ⚠️ Identified Mission Risks\n")
        if plan.risks:
            for risk in plan.risks:
                md.append(f"- {risk}")
        else:
            md.append("- No significant operational risks identified during planning.")

        md.append("\n---\n")

        # Confidence Assessment
        md.append("## 📊 Mission Confidence Assessment\n")
        md.append(f"**Overall Confidence Score:** `{plan.confidence_score}/100`\n")

        if plan.confidence_score >= 80:
            md.append(
                "The mission plan demonstrates a high probability of success. "
                "Resource allocation, hazard avoidance, and scientific prioritization "
                "are well aligned with mission constraints."
            )
        elif plan.confidence_score >= 60:
            md.append(
                "The mission is feasible but presents moderate operational risks. "
                "Careful execution and continuous monitoring are recommended."
            )
        else:
            md.append(
                "The mission plan carries significant risk. "
                "Re-evaluation of targets, routing, or resource allocation is advised."
            )

        # Write file
        output_path = Path("outputs/mission_plan.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(md), encoding="utf-8")

        print(f"Mission Plan successfully saved to {output_path}")



def test_mission():
    flow = MissionTestFlow()
    flow.kickoff()
    print("\nMission Crew process completed successfully")

if __name__ == "__main__":
    test_mission()