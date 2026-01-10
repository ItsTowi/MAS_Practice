import sys
import os
from pathlib import Path
from crewai.flow.flow import Flow, listen, start
import json
from mars_exploration.crews.drone_crew.drone_crew import DroneCrew

# --- MOCK INPUT ---
# Simulamos lo que la Mission Crew nos enviaría.
# Esto nos permite probar los drones sin ejecutar la Mission Crew real.
MOCK_MISSION_PLAN = """
# Mission Strategic Plan

## Scientific Objectives
1. High Priority: Capture high-resolution images of the rock formation at **N52**.
2. Medium Priority: Perform aerial survey of the crater edge at **N3**.
3. Low Priority: Data collection at **N24**.

## Hazards Identified
- **Dust Storm** detected approaching sector **N10**.
- **Radiation** spikes near node **N99**.
- **Steep cliffs** detected at edge connecting N1 and N2.

## Operational Constraints
- Maintain minimum altitude of 50m.
- Avoid flight paths through hazard zones.
"""

class DroneTestFlow(Flow):
    """
    Test Flow specifically for the Drone Crew
    """

    @start()
    def initialize_drone_mission(self):
        """
        Unit Test: The Drone Crew plans routes based on a simulated Mission Report
        """
        print("Starting Drone Crew Test Flow...\n")
        
        # 1. Verificamos que existan los archivos que usan las TOOLS (no son inputs directos, pero sin ellos falla)
        required_files = [
            "src/mars_exploration/inputs/drones.json",
            "src/mars_exploration/inputs/mars_terrain.graphml"
        ]

        print("Verifying Tool Dependencies...")
        for path in required_files:
            if not Path(path).exists():
                raise FileNotFoundError(f"Required tool dependency file not found: {path}")
            print(f"Verified: {path}")

        # 2. Preparamos el input (Simulado)
        inputs = {
            "mission_report": MOCK_MISSION_PLAN
        }

        try:
            print("\nKickoff Drone Crew with Mock Mission Plan...")
            # Ejecutamos el crew
            result = DroneCrew().crew().kickoff(inputs=inputs)

            # 3. Extraemos el Pydantic (Estructurado)
            structured_plan = None
            if hasattr(result, 'pydantic'):
                structured_plan = result.pydantic
            elif hasattr(result, 'tasks_output') and len(result.tasks_output) > 0:
                # A veces el output pydantic está en la última tarea si el kickoff global no lo pilla
                last_task = result.tasks_output[-1]
                if hasattr(last_task, 'pydantic'):
                    structured_plan = last_task.pydantic

            # Fallback a diccionario si es necesario
            if structured_plan is None and isinstance(result, dict):
                structured_plan = result
        
            return {
                "structured_plan": structured_plan,
                "raw_output": result.raw if hasattr(result, 'raw') else str(result),
                "inputs": inputs
            }
        except Exception as e:
            print(f"\nError during Drone Crew execution: {e}")
            raise
    
    
    @listen(initialize_drone_mission)
    def validate_and_save_drone_plan(self, drone_data: dict):
        """
        Validate the generated flight assignments and save them.
        """
        print("\nDrone Plan Output Analysis:\n")

        structured_plan = drone_data["structured_plan"]
        validation_passed = True

        # 1. Basic Validation
        if structured_plan is None:
            print("❌ Validation failed: No structured plan generated (Pydantic object missing)")
            validation_passed = False
        else:
            print("✅ Structured plan generated successfully")

            # 2. Check for Assignments (Esto depende de tu modelo Pydantic en drone_crew.py)
            # Asumiendo que tu modelo tiene un campo 'assignments' o 'flight_paths'
            
            # Intentamos acceder como objeto o como diccionario
            assignments = []
            if hasattr(structured_plan, 'assignments'):
                assignments = structured_plan.assignments
            elif isinstance(structured_plan, dict) and 'assignments' in structured_plan:
                assignments = structured_plan['assignments']
            
            if len(assignments) > 0:
                print(f"✅ Drone Assignments created: {len(assignments)}")
                
                # Validar contenido de un assignment
                first_assign = assignments[0]
                # Chequeo flexible (si es objeto o dict)
                drone_id = getattr(first_assign, 'drone_id', None) or first_assign.get('drone_id')
                path = getattr(first_assign, 'path_nodes', None) or first_assign.get('path_nodes')
                dist = getattr(first_assign, 'total_distance', None) or first_assign.get('total_distance')

                if drone_id and path:
                    print(f"✅ Data Integrity Check Passed (ID: {drone_id}, Path found)")
                else:
                    print("⚠️ Warning: Missing critical fields in assignment data")
                    validation_passed = False
                
                # Chequeo de seguridad básico
                if dist and dist > 30: # Asumiendo 30 como rango máximo de ejemplo
                    print(f"⚠️ Warning: Drone {drone_id} has a very long path ({dist}). Check range constraints.")
            else:
                print("⚠️ Warning: Plan generated but empty assignments list.")
                validation_passed = False

        # 3. Save Outputs
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        json_path = output_dir / "drone_plan_test.json"
        md_path = output_dir / "drone_report_test.md"

        try:
            # Guardar JSON Estructurado
            json_data = {}
            if hasattr(structured_plan, 'model_dump'):
                json_data = structured_plan.model_dump()
            elif hasattr(structured_plan, 'dict'):
                json_data = structured_plan.dict()
            else:
                json_data = {"raw": str(structured_plan)}

            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            print(f"💾 Saved JSON plan: {json_path}")
            
            # Guardar Markdown (Raw Output del Reporter)
            with open(md_path, 'w') as f:
                f.write(drone_data["raw_output"])
            print(f"💾 Saved Markdown report: {md_path}")

        except Exception as e:
            print(f"Could not save output files: {e}")

        if validation_passed:
            print("\n🟢 Drone Crew Test Validation PASSED")
        else:
            print("\n🟡 Drone Crew Test Validation COMPLETED WITH WARNINGS")

        return drone_data
    
    @listen(validate_and_save_drone_plan)
    def display_drone_summary(self, drone_data: dict):
        """
        Display a human-readable summary of who is flying where.
        """
        print("\n=== 🚁 DRONE FLIGHT SUMMARY ===\n")
        
        structured_plan = drone_data["structured_plan"]
        
        # Recuperar asignaciones de nuevo para mostrar
        assignments = []
        if hasattr(structured_plan, 'assignments'):
            assignments = structured_plan.assignments
        elif isinstance(structured_plan, dict) and 'assignments' in structured_plan:
            assignments = structured_plan['assignments']

        if not assignments:
            print("No flights scheduled.")
            return

        for job in assignments:
            # Acceso seguro a atributos
            d_id = getattr(job, 'drone_id', 'Unknown')
            tgt = getattr(job, 'target_id', 'Unknown')
            dist = getattr(job, 'total_distance', 0)
            path = getattr(job, 'path_nodes', [])
            
            print(f"🔹 {d_id} -> Target: {tgt}")
            print(f"   Route: {path}")
            print(f"   Distance: {dist} km")
            print("   -----------------------------")

        print("\nTest Flow Execution Complete.")

def initialize_drone_mission():
    """
    Función de entrada para el comando 'crewai test'.
    Instancia el flujo y lo ejecuta.
    """
    flow = DroneTestFlow()
    flow.kickoff()

def test_drones():
    """
    Alias por si acaso quieres llamarlo de otra forma manualmente.
    """
    initialize_drone_mission()

if __name__ == "__main__":
    test_drones()