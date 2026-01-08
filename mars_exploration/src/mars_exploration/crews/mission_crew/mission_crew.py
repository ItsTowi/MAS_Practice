from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from mars_exploration.tools.markdown import MarkdownReaderTool
from mars_exploration.tools.graphTool import GraphMLReaderTool

# Pydantic Outputs
class MissionReportSummary(BaseModel):
    objectives: List[Dict[str, str]] = Field(description="List of objectives with node, task, and terrain.")
    constraints: Dict[str, float] = Field(description="Operational limits (e.g., battery threshold, flight time).")
    priorities: Dict[str, List[str]] = Field(description="High, Medium, and Low priority node lists.")

class HazardAssessmentOutput(BaseModel):
    restricted_nodes: List[str] = Field(description="List of prohibited node IDs.")
    hazard_details: Dict[str, str] = Field(description="Map of node ID to its hazard type (e.g., {'N88': 'radiation'})")

# Optimized resources
class ResourceOptimizationOutput(BaseModel):
    allocation_strategy: str = Field(description="Strategic advice on energy and time management.")
    bottlenecks: List[str] = Field(description="Potential risks regarding battery or mission duration.")

# Refined scientific prioritization
class ScientificPrioritizationOutput(BaseModel):
    ranked_targets: List[str] = Field(description="Final ordered list of nodes based on value vs safety.")
    justification: str = Field(description="Reasoning for re-prioritizing or skipping certain nodes.")


class ActionStep(BaseModel):
    unit: str = Field(description="Rover, Drone, or Satellite")
    node: str = Field(description="Target node ID")
    action: str = Field(description="Specific task to perform (e.g., sample collection)")
    rationale: str = Field(description="Brief explanation of why this action is prioritized.")

class MasterMissionPlan(BaseModel):
    plan_name: str
    approved_targets: List[str]
    no_go_zones: List[str]
    action_sequence: List[ActionStep]
    emergency_protocols: List[str]
    markdown_report: str = Field(description="The full Markdown formatted report text")


@CrewBase
class MissionCrew():
    """Mission Crew for Mars Exploration."""

    current_dir = Path(__file__).resolve().parent
    print(f"Current directory: {current_dir}")

    agents_config = 'config/mission_agent.yaml'
    tasks_config = 'config/mission_tasks.yaml'

    def __init__(self) -> None:
        self.llm = 'ollama/qwen3:4b'
        #self.llm = 'gemini/gemini-2.5-flash'
        self.markdown_tool = MarkdownReaderTool()
        self.graphml_tool = GraphMLReaderTool()

    @agent
    def mission_planner(self) -> Agent:
        """
        Central Brain
        """
        return Agent(
            config=self.agents_config['mission_planner'], 
            llm=self.llm,
            tools=[self.markdown_tool],
            verbose=False
        )
    
    @agent
    def hazard_assessment(self) -> Agent:
        """
        Safety Specialist
        """
        return Agent(
            config=self.agents_config['hazard_assessment'],
            llm=self.llm,
            tools=[self.markdown_tool, self.graphml_tool],
            verbose=False,
            allow_delegation=False
        )
    
    @agent
    def resource_optimization(self) -> Agent:
        """
        Efficiecny expert
        """
        return Agent(
            config=self.agents_config['resource_optimization'],
            llm=self.llm,
            tools=[self.markdown_tool, self.graphml_tool],
            verbose=False,
            allow_delegation=False
        )
    
    @agent
    def scientific_target_evaluator(self) -> Agent:
        """
        Science prioritizer
        """
        return Agent(
            config=self.agents_config['scientific_target_evaluator'],
            llm=self.llm,
            tools=[self.markdown_tool, self.graphml_tool],
            verbose=False,
            allow_delegation=False
        )
    
    @agent
    def decision_synthesizer(self) -> Agent:
        """
        Final integrator
        """
        return Agent(
            config=self.agents_config['decision_synthesizer'],
            llm=self.llm,
            verbose=False,
            allow_delegation=True
        )
    

    @task
    def analyze_mission_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_mission_report_task'],
            output_pydantic=MissionReportSummary
            )

    
    @task
    def assess_hazard_task(self) -> Task:
        return Task(
            config=self.tasks_config['assess_hazards_task'],
            output_pydantic=HazardAssessmentOutput,
        )
    
    @task
    def optimize_resources_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_resources_task'],
            context=[self.analyze_mission_report_task()],
            output_pydantic=ResourceOptimizationOutput
        )
    
    @task
    def prioritize_science_task(self) -> Task:
        return Task(
            config=self.tasks_config['prioritize_science_task'],
            context=[
                self.analyze_mission_report_task(),
                self.assess_hazard_task()
            ],
            output_pydantic=ScientificPrioritizationOutput
        )
    
    @task
    def synthesize_final_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_final_plan_task'],
            context=[
                self.prioritize_science_task(), 
                self.optimize_resources_task(), 
                self.assess_hazard_task()
            ],
            output_pydantic=MasterMissionPlan,
            output_file='outputs/mission_plan.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """
        Mission Crew
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        

    
