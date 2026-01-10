from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class SatelliteCrew:
    """Satellite Crew for Mars Exploration"""

    agents_config = "config/satelite_agent.yaml"
    tasks_config = "config/satelite_tasks.yaml"

    def __init__(self) -> None:
        self.llm = "ollama/qwen3:4b"
        self.mars_root = Path(__file__).resolve().parents[4]  # mars_exploration/
        # Optional tools could be added here (same pattern as RoverCrew)

    # ---------------- Agents ----------------
    @agent
    def orbit_planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["orbit_planning_agent"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def orbital_imaging_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["orbital_imaging_agent"],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def communication_relay_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["communication_relay_agent"],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def environment_monitoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["environment_monitoring_agent"],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def satellite_coordination_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["satellite_coordination_agent"],
            llm=self.llm,
            verbose=True,
        )

    # ---------------- Tasks ----------------
    @task
    def analyze_mission_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_mission_plan_task"],
            agent=self.satellite_coordination_agent(),
        )

    @task
    def orbit_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["orbit_planning_task"],
            agent=self.orbit_planning_agent(),
        )

    @task
    def orbital_imaging_task(self) -> Task:
        return Task(
            config=self.tasks_config["orbital_imaging_task"],
            agent=self.orbital_imaging_agent(),
        )

    @task
    def communication_relay_task(self) -> Task:
        return Task(
            config=self.tasks_config["communication_relay_task"],
            agent=self.communication_relay_agent(),
        )

    @task
    def environment_monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config["environment_monitoring_task"],
            agent=self.environment_monitoring_agent(),
        )

    @task
    def generate_satellite_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_satellite_plan_task"],
            agent=self.satellite_coordination_agent(),
            output_file="crews/satelite_crew/outputs/satellite_plan.md",
        )


    # ---------------- Crew ----------------
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            embedder={"provider": "ollama", "config": {"model": "nomic-embed-text:latest"}},
        )