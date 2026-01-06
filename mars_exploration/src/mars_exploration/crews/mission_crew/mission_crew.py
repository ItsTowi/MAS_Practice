from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path


## Pydantic Output Models
class MissionReportSummary(BaseModel):
    mission_duration_sols: int = Field(description="Total mission duration in Martian sols")
    primary_objectives: List[str] = Field(description="List of primary mission objectives")
    operational_constraints: Dict[str, str] = Field(description="Key operational constraints")
    communication_windows: List[str] = Field(description="Available communication windows")
    known_hazards: List[str] = Field(description="Initially known hazards from the report")


class HazardZone(BaseModel):
    zone_id: str = Field(description="ID for the hazard Zone")
    hazard_type: str = Field(description="Type of hazard (dust_storm, radiation, cliff, etc.)")
    risk_level: str = Field(description="Risk Level: low, medium, high, critical")
    affected_nodes: List[str] = Field(description="List of node IDs affected by this hazard")
    time_window: Optional[str] = Field(default=None, description="Time period when hazard is active")
    recommendation: str = Field(description="Safety recommendation for affected areas")

class HazardAssessmentOutput(BaseModel):
    hazard_zones: List[HazardZone] = Field(description="Detailed list of all hazard zones")
    safe_zones: List[str] = Field(description="List of verified safe node IDs")
    restricted_nodes: List[str] = Field(description="Nodes that should be avoided")
    emergency_protocols: Dict[str, str] = Field(description="Protocol per hazard type")


class ResourceAllocation(BaseModel):
    resource_type: str = Field(description="Type of resource (energy, bandwidth, time)")
    total_available: float = Field(description="Total amount available")
    allocated_to_rovers: float = Field(description="Amount allocated to rovers")
    allocated_to_drones: float = Field(description="Amount allocated to drones")
    allocated_to_satellites: float = Field(description="Amount allocated to satellites")
    buffer_reserve: float = Field(description="Reserve buffer for contingencies")

class ResourceOptimizationOutput(BaseModel):
    allocations: List[ResourceAllocation] = Field(description="Resource allocation breakdown")
    bottleneck_warnings: List[str] = Field(description="Identified potential bottlenecks")
    optimization_recommendations: List[str] = Field(description="Recommendations to improve efficiency")


class ScientificObjective(BaseModel):
    id: str = Field(description="Unique identifier for the objective")
    name: str = Field(description="Name of the scientific objective")
    priority: int = Field(description="Priority level (1-10, where 10 is highest)")
    target_location: str = Field(description="Target location or node ID")
    scientific_value: float = Field(description="Scientific value score (0-100)")
    justification: str = Field(description="Reasoning for the priority assignment")


class ScientificPrioritizationOutput(BaseModel):
    prioritized_objectives: List[ScientificObjective] = Field(description="Ranked scientific objectives")
    high_value_targets: List[str] = Field(description="Top priority target locations")
    backup_targets: List[str] = Field(description="Alternative targets if primary fails")

class MasterMissionPlan(BaseModel):
    mission_summary: str = Field(description="Executive summary of the mission plan")
    scientific_priorities: List[ScientificObjective] = Field(description="Final prioritized objectives")
    hazard_zones: List[HazardZone] = Field(description="All identified hazard zones")
    resource_allocations: List[ResourceAllocation] = Field(description="Final resource distribution")
    restricted_areas: List[str] = Field(description="Areas to avoid")
    safe_routes: List[str] = Field(description="Recommended safe paths/zones")
    critical_constraints: List[str] = Field(description="Must-follow constraints")
    contingency_plans: Dict[str, str] = Field(description="Backup plans for common scenarios")



@CrewBase
class MissionCrew():
    """Mission Crew for Mars Exploration."""

    current_dir = Path(__file__).resolve().parent
    print(f"Current directory: {current_dir}")

    agents_config = 'config/mission_agent.yaml'
    tasks_config = 'config/mission_tasks.yaml'

    def __init__(self, mission_report_path: str = None, terrain_data_path: str = None) -> None:
        #self.llm = 'ollama/qwen3:4b'
        self.llm = 'gemini/gemini-2.5-flash'

    @agent
    def mission_planner(self) -> Agent:
        """
        Central Brain
        """
        return Agent(
            config=self.agents_config['mission_planner'], 
            llm=self.llm,
            verbose=True)
    
    @agent
    def hazard_assessment(self) -> Agent:
        """
        Safety Specialist
        """
        return Agent(
            config=self.agents_config['hazard_assessment'],
            llm=self.llm, 
            verbose=True)
    
    @agent
    def resource_optimization(self) -> Agent:
        """
        Efficiecny expert
        """
        return Agent(
            config=self.agents_config['resource_optimization'],
            llm=self.llm,
            verbose=True)
    
    @agent
    def scientific_target_evaluator(self) -> Agent:
        """
        Science prioritizer
        """
        return Agent(
            config=self.agents_config['scientific_target_evaluator'],
            llm=self.llm,
            verbose=True)
    
    @agent
    def decision_synthesizer(self) -> Agent:
        """
        Final integrator
        """
        return Agent(
            config=self.agents_config['decision_synthesizer'],
            llm=self.llm,
            verbose=True)
    

    @task
    def analyze_mission_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_mission_report_task'],
            output_pydantic=MissionReportSummary)
    
    @task
    def assess_hazard_task(self) -> Task:
        return Task(
            config=self.tasks_config['assess_hazards_task'],
            output_pydantic=HazardAssessmentOutput)
    
    @task
    def optimize_resources_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_resources_task'],
            output_pydantic=ResourceOptimizationOutput)
    
    @task
    def prioritize_science_task(self) -> Task:
        return Task(
            config=self.tasks_config['prioritize_science_task'],
            output_pydantic=ResourceOptimizationOutput)
    
    @task
    def synthesize_final_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_final_plan_task'],
            output_pydantic=MasterMissionPlan,
            output_file='outputs/structured_mission_plan.md'    ,
            context=[
                self.analyze_mission_report_task(),
                self.assess_hazard_task(),
                self.optimize_resources_task(),
                self.prioritize_science_task()
            ]
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
        

    
