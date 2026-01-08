from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from enum import Enum
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from mars_exploration.tools.markdown import MarkdownReaderTool
from mars_exploration.tools.graphTool import GraphMLReaderTool

class MissionObjective(BaseModel):
    node_id: str
    task: str
    priority: str
    science_value: int = Field(ge=1, le=10)
    duration_min: int
    allowed_units: List[str]

class Constraint(BaseModel):
    unit: str
    type: str  # energy, time, communication, environment
    limit: float
    critical: float
    recovery: str

class Hazard(BaseModel):
    node_id: str
    type: str
    severity: Literal["low", "medium", "high", "critical"]
    mitigation: str

class MissionReportSummary(BaseModel):
    mission_id: str = Field(
        default_factory=lambda: f"MARS-{datetime.now().strftime('%Y%m%d-%H%M')}"
    )
    objectives: List[MissionObjective]
    constraints: List[Constraint]
    total_duration_hours: float

class HazardAssessmentOutput(BaseModel):
    restricted_nodes: List[str]
    hazards: List[Hazard]
    safe_paths: List[List[str]]

class UnitPlan(BaseModel):
    unit: str
    assigned_nodes: List[str]
    energy_used: float
    time_used: float

class ResourceOptimizationOutput(BaseModel):
    unit_plans: List[UnitPlan]
    bottlenecks: List[str]
    efficiency_score: float = Field(ge=0, le=100)

class RankedTarget(BaseModel):
    node_id: str
    score: float = Field(ge=0, le=10)
    recommended_unit: str
    reason: str

class ScientificPrioritizationOutput(BaseModel):
    ranked_targets: List[RankedTarget]
    deferred: List[str]

class Action(BaseModel):
    step: int
    unit: str
    node: str
    task: str
    duration_min: int

class MasterMissionPlan(BaseModel):
    mission_id: str
    approved_nodes: List[str]
    actions: List[Action]
    risks: List[str]
    confidence_score: float = Field(ge=0, le=100)

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
        

    
