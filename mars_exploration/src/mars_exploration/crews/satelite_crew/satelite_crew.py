from __future__ import annotations
from typing import Any, Dict

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .contracts import extract_mission_context, satellite_output_contract
from .planning import (
    build_orbit_plan,
    build_imaging_plan,
    build_communication_plan,
    build_environment_report,
    export_artifacts,
)

@CrewBase
class SatelliteCrew:
    """
    CrewAI Satellite Crew (Task 3 requirement).
    We keep deterministic planning (option 1) to ensure stable integration with other crews.
    """

    # Usa tus stand-in ya creados:
    agents_config = "config/satellite_agent.yaml"
    tasks_config = "config/satellite_task.yaml"

    # ---- Agents (exist for CrewAI structure; deterministic logic is in planning.py) ----
    @agent
    def orbital_imaging_agent(self) -> Agent:
        return Agent(config=self.agents_config["orbital_imaging_agent"])

    @agent
    def communication_relay_agent(self) -> Agent:
        return Agent(config=self.agents_config["communication_relay_agent"])

    @agent
    def orbit_planning_agent(self) -> Agent:
        return Agent(config=self.agents_config["orbit_planning_agent"])

    @agent
    def environment_monitoring_agent(self) -> Agent:
        return Agent(config=self.agents_config["environment_monitoring_agent"])

    @agent
    def satellite_coordination_agent(self) -> Agent:
        return Agent(config=self.agents_config["satellite_coordination_agent"])

    # ---- Tasks (we define them to satisfy MAS structure; outputs are produced deterministically) ----
    @task
    def orbit_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["orbit_planning_task"],
            agent=self.orbit_planning_agent(),
        )

    @task
    def environment_monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config["environment_monitoring_task"],
            agent=self.environment_monitoring_agent(),
        )

    @task
    def orbital_imaging_task(self) -> Task:
        return Task(
            config=self.tasks_config["orbital_imaging_task"],
            agent=self.orbital_imaging_agent(),
            context=[self.orbit_planning_task(), self.environment_monitoring_task()],
        )

    @task
    def communication_relay_task(self) -> Task:
        return Task(
            config=self.tasks_config["communication_relay_task"],
            agent=self.communication_relay_agent(),
            context=[self.orbit_planning_task(), self.environment_monitoring_task()],
        )

    @task
    def satellite_coordination_task(self) -> Task:
        return Task(
            config=self.tasks_config["satellite_coordination_task"],
            agent=self.satellite_coordination_agent(),
            context=[
                self.orbit_planning_task(),
                self.environment_monitoring_task(),
                self.orbital_imaging_task(),
                self.communication_relay_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        # Sequential matches your Task 1 narrative and is simplest for evaluation
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def run_satellite_crew(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stable entry point for Flow/main.py:
    - consumes mission_context (from Mission Crew, or stand-in)
    - returns a stable output contract for Integration Crew
    """
    ctx = extract_mission_context(inputs)

    plan = {
        "orbit": build_orbit_plan(ctx),
        "imaging": build_imaging_plan(ctx),
        "communications": build_communication_plan(ctx),
        "environment": build_environment_report(ctx),
        "notes": [
            "CrewAI SatelliteCrew wrapper with deterministic planning (stable for team integration)."
        ],
        "inputs_used": ctx,
    }

    artifacts = export_artifacts(plan)
    return satellite_output_contract(plan=plan, artifacts=artifacts)
