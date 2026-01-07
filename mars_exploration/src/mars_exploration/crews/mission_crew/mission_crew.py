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

# Represents what was extracted from the Markdown
class MissionReportSummary(BaseModel):
    objectives: List[Dict[str, str]] = Field(description="List of objectives with their location and terrain")
    constraints: List[str] = Field(description="Key operational constraints")
    priorities: Dict[str, List[str]] = Field(description="Priorities by level (High, Medium, Low)")
    known_hazards: List[str] = Field(description="Initial hazards mentioned")

# Risk assessment by the Hazard Agent
class HazardZone(BaseModel):
    node: str = Field(description="Node ID")
    hazard_type: str = Field(description="Type of hazard (unstable, radiation, storm)")
    risk_level: str = Field(description="Risk level")

class HazardAssessmentOutput(BaseModel):
    hazards: List[HazardZone]
    restricted_nodes: List[str] = Field(description="Prohibited nodes")

# Optimized resources
class ResourceOptimizationOutput(BaseModel):
    allocations: Dict[str, str] = Field(description="Energy/time allocation per agent type")
    warnings: List[str] = Field(description="Potential bottlenecks")

# Refined scientific prioritization
class ScientificPrioritizationOutput(BaseModel):
    ranked_targets: List[str] = Field(description="Nodes ordered by actual scientific value")
    justification: str

class ActionStep(BaseModel):
    unit: str = Field(description="Rover or Drone")
    target_node: str
    action: str
    constraints: Optional[str] = None

class MasterMissionPlan(BaseModel):
    mission_overview: str = Field(description="High-level summary of the mission")
    final_targets: List[str] = Field(description="Ordered list of approved mission targets")
    no_go_zones: List[str] = Field(description="List of restricted/hazardous nodes")
    resource_plan: Dict[str, str] = Field(description="Resource allocation strategy")
    action_plan: List[ActionStep] = Field(description="Sequential action steps for mission execution")
    risk_notes: List[str] = Field(description="Key risks and mitigation strategies")


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
        self.makdown_tool = MarkdownReaderTool()
        self.graphml_tool = GraphMLReaderTool()

    @agent
    def mission_planner(self) -> Agent:
        """
        Central Brain
        """
        return Agent(
            config=self.agents_config['mission_planner'], 
            llm=self.llm,
            tools=[self.makdown_tool, self.graphml_tool],
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
            tools=[self.graphml_tool],
            verbose=False
        )
    
    @agent
    def resource_optimization(self) -> Agent:
        """
        Efficiecny expert
        """
        return Agent(
            config=self.agents_config['resource_optimization'],
            llm=self.llm,
            tools=[self.makdown_tool, self.graphml_tool],
            verbose=False
        )
    
    @agent
    def scientific_target_evaluator(self) -> Agent:
        """
        Science prioritizer
        """
        return Agent(
            config=self.agents_config['scientific_target_evaluator'],
            llm=self.llm,
            tools=[self.makdown_tool, self.graphml_tool],
            verbose=False
        )
    
    @agent
    def decision_synthesizer(self) -> Agent:
        """
        Final integrator
        """
        return Agent(
            config=self.agents_config['decision_synthesizer'],
            llm=self.llm,
            verbose=False
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
            output_pydantic=ResourceOptimizationOutput,
        )
    
    @task
    def prioritize_science_task(self) -> Task:
        return Task(
            config=self.tasks_config['prioritize_science_task'],
            output_pydantic=ScientificPrioritizationOutput
        )
    
    @task
    def synthesize_final_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_final_plan_task'],
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
        

    
