import sys
import os
from pathlib import Path
from crewai.flow.flow import Flow, listen, start
from datetime import datetime

# Asegúrate de que Python encuentre tu módulo base
# sys.path.append(os.path.abspath("../..")) 

from mars_exploration.crews.integration_crew.integration_crew import IntegrationCrew

class IntegrationTestFlow(Flow):
    """
    Test Flow for Integration Crew.
    Simulates the reception of data from Rover, Drone, and Satellite crews
    and validates the generation of the Master Mission Plan.
    """

    def _read_or_mock_input(self, file_path: str, mock_data: str) -> str:
        """Helper to read a file if it exists, otherwise return mock data."""
        path = Path(file_path)
        if path.exists():
            print(f"📂 Loading real input from: {file_path}")
            return path.read_text(encoding='utf-8')
        else:
            print(f"⚠️ File {file_path} not found. Using MOCK data.")
            return mock_data

    @start()
    def run_integration_logic(self):
        print("🚀 Starting Integration Crew Test Flow...\n")

        # 1. Definimos datos simulados (Mock) por si no existen los archivos reales.
        # Esto es vital para probar tu crew independientemente de las otras.
        
        mock_rover = """
        [ROVER REPORT]
        - RVR-01: Location Node_Alpha, Battery 85%, Status: OPERATIONAL.
        - RVR-02: Location Node_Beta, Battery 12%, Status: CRITICAL (Low Energy).
        Samples collected: 3. Hazards encountered: None.
        """

        mock_drone = """
        [DRONE REPORT]
        - DRN-01: Flight Status AIRBORNE. Area Mapped: Sector_B (Nodes 5, 6, 7).
        - Hazards Detected: Dust Storm approaching Sector_C (High Severity).
        """

        mock_satellite = """
        [SATELLITE REPORT]
        - SAT-01: Orbit Stable. Communication Window: 14:00 - 16:00 UTC.
        - Imaging: Completed for Sector_B.
        """

        # 2. Preparamos los inputs (Intentando leer archivos reales primero)
        inputs = {
            "rover_report": self._read_or_mock_input("outputs/rover_operation_plan.md", mock_rover),
            "drone_report": self._read_or_mock_input("outputs/drone_output.md", mock_drone),
            "satellite_report": self._read_or_mock_input("outputs/satellite_plan.md", mock_satellite),
            "mission_goals": "Primary Goal: Analyze rock composition in Sector B. Secondary: Map Sector C."
        }

        try:
            # Ejecutamos la Integration Crew
            # Nota: Al usar kickoff, CrewAI ejecutará tu lógica secuencial y 
            # generará automáticamente el archivo 'outputs/final_mission.md' 
            # porque lo definimos en el task 'coordinate_mission_task'.
            result = IntegrationCrew().crew().kickoff(inputs=inputs)
            return result
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            raise

    @listen(run_integration_logic)
    def validate_results(self, crew_output):
        print("\n✅ Integration Process Completed!")
        
        # 1. Validar el Objeto Pydantic (MasterMissionPlan)
        
        
        if crew_output.pydantic:
            plan = crew_output.pydantic
            print("\n--- 🧠 Structured Data (Pydantic) ---")
            print(f"Mission Phase: {plan.mission_phase}")
            print(f"Strategic Objective: {plan.strategic_objective}")
            print(f"Risk Assessment: {plan.risk_assessment}")
            print(f"Planned Actions: {len(plan.sequence_of_events)} steps generated.")
            
            # Imprimir un par de acciones para verificar
            for action in plan.sequence_of_events[:2]: 
                print(f"   -> Step {action.step_id}: {action.agent_id} will {action.action} at {action.target}")
        else:
            print("⚠️ Warning: No Pydantic output received.")
        # 2. Validar que el archivo Markdown se haya creado
        output_file = Path("outputs/final_mission.md")
        if output_file.exists():
            print(f"\n📄 Success: Output file found at {output_file}")
            print("--- Preview of Markdown content (First 500 chars) ---")
            print(output_file.read_text(encoding='utf-8')[:500])
            print("...\n")
        else:
            print(f"\n❌ Error: The file {output_file} was NOT created.")

def test_integration():
    flow = IntegrationTestFlow()
    flow.kickoff()

if __name__ == "__main__":
    test_integration()