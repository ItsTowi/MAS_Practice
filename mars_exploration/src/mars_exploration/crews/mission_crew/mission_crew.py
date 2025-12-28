from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os

from pathlib import Path

@CrewBase
class MissionCrew():
    """Mission Crew for Mars Exploration."""

    current_dir = Path(__file__).resolve().parent
    print(f"Current directory: {current_dir}")

    agents_config = 'config/mission_agent.yaml'
    tasks_config = 'config/mission_tasks.yaml'

    def __init__(self) -> None:
        self.llm = 'ollama/qwen3:4b'

    @agent
    def mission_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['mission_planner'], 
            llm=self.llm,
            verbose=True)
    
    @agent
    def hazard_assessment(self) -> Agent:
        return Agent(
            config=self.agents_config['hazard_assessment'],
            llm=self.llm, 
            verbose=True)
    
    @agent
    def resource_optimization(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_optimization'],
            llm=self.llm,
            verbose=True)
    
    @agent
    def scientific_target_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['scientific_target_evaluator'],
            llm=self.llm,
            verbose=True)
    
    @agent
    def decision_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['decision_synthesizer'],
            llm=self.llm,
            verbose=True)
    

    @task
    def analyze_mission_report_task(self) -> Task:
        return Task(config=self.tasks_config['analyze_mission_report_task'])
    
    @task
    def assess_hazard_task(self) -> Task:
        return Task(config=self.tasks_config['assess_hazards_task'])
    
    @task
    def prioritize_science_task(self) -> Task:
        return Task(config=self.tasks_config['prioritize_science_task'])
    
    @task
    def synthesize_final_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_final_plan_task'],
            output_file='outputs/structured_mission_plan.md'    
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        

    
