from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class SatelliteCrew:
    """Satellite Crew for Mars Exploration"""

    agents_config = "config/satellite_agent.yaml"
    tasks_config = "config/satellite_tasks.yaml"

    def __init__(self) -> None:
        self.llm = "ollama/qwen3:4b"
        # Tools are optional; keep pattern consistent with others
        self.satellite_info_tool = None

        # If you later have tools, import them here like RoverCrew does:
        # try:
        #     from mars_exploration.tools.satellite_tools import SatelliteInfoTool
        #     self.satellite_info_tool = SatelliteInfoTool()
        # except Exception:
        #     self.satellite_info_tool = None

    # ---------------- Agents ----------------
    @agent
    def satellite_coordination_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["satellite_coordination_agent"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def orbit_planning_agent(self) -> Agent:
        tools = [t for t in [self.satellite_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["orbit_planning_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def orbital_imaging_agent(self) -> Agent:
        tools = [t for t in [self.satellite_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["orbital_imaging_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def communication_relay_agent(self) -> Agent:
        tools = [t for t in [self.satellite_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["communication_relay_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def environment_monitoring_agent(self) -> Agent:
        tools = [t for t in [self.satellite_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["environment_monitoring_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    # ---------------- Tasks ----------------
    @task
    def analyze_mission_plan_task(self) -> Task:
        return Task(config=self.tasks_config["analyze_mission_plan_task"])

    @task
    def orbit_planning_task(self) -> Task:
        return Task(config=self.tasks_config["orbit_planning_task"])

    @task
    def orbital_imaging_task(self) -> Task:
        return Task(config=self.tasks_config["orbital_imaging_task"])

    @task
    def communication_relay_task(self) -> Task:
        return Task(config=self.tasks_config["communication_relay_task"])

    @task
    def environment_monitoring_task(self) -> Task:
        return Task(config=self.tasks_config["environment_monitoring_task"])

    @task
    def generate_satellite_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_satellite_plan_task"],
            output_file="outputs/satellite_plan.md",
        )

    # ---------------- Crew ----------------
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            embedder={
                "provider": "ollama",
                "config": {"model": "nomic-embed-text:latest"},
            },
        )
