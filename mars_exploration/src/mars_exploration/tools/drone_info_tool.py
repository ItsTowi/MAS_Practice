import json
from crewai_tools import BaseTool

class DroneInfoTool(BaseTool):
    name: str = "Drone Info Reader"
    description: str = "Reads the technical specifications (ID, range, camera resolution) and current location of all available drones from the JSON file."

    def _run(self, file_path: str = 'drones.json') -> str:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error reading drone file: {str(e)}"