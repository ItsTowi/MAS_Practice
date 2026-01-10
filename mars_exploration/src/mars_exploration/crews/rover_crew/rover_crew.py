from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class RoverCrew:
    """Rover Crew for Mars Exploration"""

    agents_config = "config/rover_agent.yaml"
    tasks_config = "config/rover_tasks.yaml"

    def __init__(self) -> None:
        self.llm = "ollama/qwen3:4b"
        self.node_distance_tool = None
        self.rover_info_tool = None

        # Tools are optional; the crew must still run even if tools are unavailable.
        try:
            from mars_exploration.tools.drone_tools import NodeDistanceTool
            self.node_distance_tool = NodeDistanceTool()
        except Exception:
            self.node_distance_tool = None

    # ---------------- Agents ----------------
    @agent
    def rover_coordinator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["rover_coordinator_agent"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def terrain_analysis_agent(self) -> Agent:
        tools = [t for t in [self.node_distance_tool, self.rover_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["terrain_analysis_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def pathfinding_agent(self) -> Agent:
        tools = [t for t in [self.node_distance_tool, self.rover_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["pathfinding_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def energy_management_agent(self) -> Agent:
        tools = [t for t in [self.rover_info_tool] if t is not None]
        return Agent(
            config=self.agents_config["energy_management_agent"],
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def rover_reporter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["rover_reporter_agent"],
            llm=self.llm,
            verbose=True,
        )

    # ---------------- Tasks ----------------
    @task
    def analyze_rover_objectives_task(self) -> Task:
        return Task(config=self.tasks_config["analyze_rover_objectives_task"])

    @task
    def terrain_traversability_task(self) -> Task:
        return Task(config=self.tasks_config["terrain_traversability_task"])

    @task
    def plan_rover_routes_task(self) -> Task:
        # IMPORTANT: no output_pydantic (prevents LiteLLM/Ollama JSON conversion crash)
        return Task(config=self.tasks_config["plan_rover_routes_task"])

    @task
    def estimate_energy_budget_task(self) -> Task:
        # IMPORTANT: no output_pydantic (prevents LiteLLM/Ollama JSON conversion crash)
        return Task(config=self.tasks_config["estimate_energy_budget_task"])

    @task
    def generate_rover_operation_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_rover_operation_plan_task"],
            output_file="outputs/rover_operation_plan.md",
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
