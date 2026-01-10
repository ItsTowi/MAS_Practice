from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

# --- SUB-MODELS FOR INDIVIDUAL STATES ---
class RoverState(BaseModel):
    id: str = Field(description="Rover ID (e.g., RVR-01)")
    location: str = Field(description="Current node ID in the graph")
    battery_level: float = Field(description="Current battery percentage")
    status: Literal['OPERATIONAL', 'CRITICAL', 'IDLE'] = Field(description="Current operational status")

class DroneState(BaseModel):
    id: str = Field(description="Drone ID")
    flight_status: str = Field(description="Grounded or Airborne")
    surveilled_area: List[str] = Field(description="List of node IDs mapped by this drone")

class Hazard(BaseModel):
    type: str = Field(description="Type of hazard (e.g., Dust Storm, Radiation, Steep Cliff)")
    affected_nodes: List[str] = Field(description="List of graph nodes affected by this hazard")
    severity: str = Field(description="High, Medium, or Low")

# --- MODEL 1: DATA FUSION (Data Fusioner) ---
class UnifiedGlobalState(BaseModel):
    """
    Represents the complete unified snapshot of the mission.
    """
    timestamp: str = Field(description="Mission time (Sol number or UTC)")
    rovers: List[RoverState] = Field(description="State of all ground units")
    drones: List[DroneState] = Field(description="State of all aerial units")
    detected_hazards: List[Hazard] = Field(description="Consolidated list of active environmental hazards")
    global_weather_status: str = Field(description="Current weather condition (e.g., Clear, Storm Approaching)")

# --- MODEL 2: ANOMALY REPORT (Anomaly Detector) ---
class AnomalyDetail(BaseModel):
    severity: Literal['CRITICAL', 'WARNING', 'INFO']
    component_id: str = Field(description="ID of the agent/vehicle involved (e.g., RVR-02)")
    issue_type: str = Field(description="Category: LOCATION_CONFLICT, RESOURCE_DEPLETION, TIMING_CLASH")
    description: str = Field(description="Detailed explanation of the anomaly")
    suggested_fix: Optional[str] = Field(description="Recommendation for the coordinator")

class DetailedAnomalyReport(BaseModel):
    """
    Detailed validation report. If is_clean is False, issues must be addressed.
    """
    is_clean: bool = Field(description="True if data is consistent enough to proceed with planning")
    validation_score: float = Field(description="Confidence score (0.0 - 1.0)")
    identified_issues: List[AnomalyDetail] = Field(description="List of specific anomalies detected")

# --- MODEL 3: MASTER PLAN (Coordinator) ---
class MissionAction(BaseModel):
    step_id: int = Field(description="Sequence number")
    agent_id: str = Field(description="Who performs the action (Rover/Drone/Sat)")
    action: str = Field(description="Action verb (MOVE, DRILL, MAP, TRANSMIT)")
    target: str = Field(description="Target node ID or object")
    start_time: str = Field(description="Estimated start time")
    duration_minutes: int = Field(description="Estimated duration")

class MasterMissionPlan(BaseModel):
    """
    Structured final deliverable defining who does what and when.
    """
    mission_phase: str = Field(description="Current mission phase (e.g., Phase 2: Exploration)")
    strategic_objective: str = Field(description="Main goal for this planning cycle")
    sequence_of_events: List[MissionAction] = Field(description="Ordered list of coordinated actions")
    resource_usage_summary: Dict[str, float] = Field(description="Est. energy consumption per rover")
    risk_assessment: str = Field(description="Final comments on mission risk level")

@CrewBase
class IntegrationCrew():
    """Integration Crew for Mars Mission"""
    
    agents_config = 'config/integration_agents.yaml'
    tasks_config = 'config/integration_tasks.yaml'
    
    # Asegúrate de que el modelo coincida con el que usáis (ej. gemini, gpt-4, etc.)
    def __init__(self) -> None:
        self.llm = 'gemini/gemini-2.5-flash' 
        
    @agent
    def data_fusioner(self) -> Agent:
        return Agent(
            config=self.agents_config['data_fusioner'], 
            llm=self.llm,
            verbose=True)
    
    @agent
    def anomaly_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['anomaly_detector'], 
            llm=self.llm,
            verbose=True)
                
    @agent
    def mission_plan_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['mission_plan_generator'], 
            llm=self.llm,
            verbose=True)
    
    @agent
    def coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['coordinator'], 
            llm=self.llm,
            verbose=True)
    
    @task
    def fuse_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['fuse_data_task'],
            output_pydantic=UnifiedGlobalState
        )
    
    @task
    def detect_anomalies_task(self) -> Task:
        return Task(
            config=self.tasks_config['detect_anomalies_task'],
            output_pydantic=DetailedAnomalyReport
        )

    @task
    def generate_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_plan_task']
        )

    @task
    def coordinate_mission_task(self) -> Task:
        return Task(
            config=self.tasks_config['coordinate_mission_task'],
            output_pydantic=MasterMissionPlan,
            output_file='outputs/final_mission.md'
        )
                
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )