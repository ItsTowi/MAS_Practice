from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List
from pydantic import BaseModel, Field
from mars_exploration.tools.drone_tools import DroneInfoTool, NodeDistanceTool

# Para cada dron necesito ID, Objetivo, Ruta, Distancia, Notas
class DroneAssignment(BaseModel):
    drone_id: str = Field(..., description="ID of the drone assigned")
    target_id: str = Field(..., description="ID or name of the target objective")
    path_nodes: List[str] = Field(..., description="List of node IDs representing the flight path")
    total_distance: float = Field(..., description="Total distance of the calculated path")
    notes: str = Field(..., description="Reason for assignment (e.g., 'Has 20MP camera for high-res requirement')")

class DroneFleetPlan(BaseModel):
    assignments: List[DroneAssignment] = Field(..., description="List of all drone assignments and paths")

@CrewBase
class DroneCrew():
    """Drone Crew for Mars Exploration"""
    
    agents_config = 'config/drone_agent.yaml'
    tasks_config = 'config/drone_tasks.yaml'

    def __init__(self) -> None:
        self.llm = 'ollama/qwen3:4b'

    # Tools
    drone_info_tool = DroneInfoTool()
    node_distance_tool = NodeDistanceTool()

    # Agentes
    @agent
    def drone_mission_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['drone_mission_analyst'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def drone_fleet_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['drone_fleet_manager'],
            # Este necesita tools de distancias y drones
            tools=[self.drone_info_tool, self.node_distance_tool],
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

    @agent
    def drone_hazard_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['drone_hazard_detector'],
            # Este solo necesita de distancias
            tools=[self.drone_info_tool],
            llm=self.llm,
            verbose=True
        )

    @agent
    def drone_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['drone_reporter'],
            llm=self.llm,
            verbose=True
        )

    # Tasks
    @task
    def analyze_mission_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_mission_task'],
        )

    @task
    def plan_routes_task(self) -> Task:
        return Task(
            config=self.tasks_config['plan_routes_task'],
            output_pydantic=DroneFleetPlan
        )

    @task
    def validate_safety_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_safety_task'],
        )

    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file='drone_mission_report.md'
        )

    # Crew
    @crew
    def crew(self) -> Crew:
        """Creates the DroneCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )