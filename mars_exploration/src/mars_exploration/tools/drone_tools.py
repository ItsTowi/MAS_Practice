import json
from crewai.tools import BaseTool
import networkx as nx
from pydantic import Field
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional

# --- 1. Schema para NodeDistanceTool (LA SOLUCIÓN AL ERROR) ---
class NodeDistanceSchema(BaseModel):
    """Input schema for NodeDistanceTool."""
    start_node: str = Field(..., description="The starting node ID (e.g., 'N1').")
    end_node: str = Field(..., description="The ending node ID (e.g., 'N52').")
    # Al usar Optional y default=None, Pydantic ya no dará error si el LLM no lo envía
    max_range: Optional[float] = Field(None, description="The maximum range of the drone. If provided, checks if distance > range.")

class DroneInfoTool(BaseTool):
    name: str = "Drone Info Reader"
    description: str = "Reads the technical specifications of the drone fleet. Returns a list of drones with their ranges and capabilities. No input required."

    def _run(self, file_path: str = None) -> str:
        try:
            # 1. Calcular la ruta absoluta basada en este archivo
            # DRONE TOOLS:  src/mars_exploration/tools/drone_tools.py
            # JSON:         src/mars_exploration/inputs/drones.json
            
            base_path = os.path.dirname(os.path.abspath(__file__)) # Carpeta tools
            # Subimos un nivel (..) y entramos a inputs
            json_path = os.path.join(base_path, '..', 'inputs', 'drones.json')
            
            # Normalizamos la ruta (quita los .. para que quede bonita)
            json_path = os.path.normpath(json_path)

            if not os.path.exists(json_path):
                return f"Error: Configuration file not found at {json_path}"

            with open(json_path, 'r') as f:
                data = json.load(f)
                
            # Convertimos a string
            return json.dumps(data, indent=2)

        except Exception as e:
            return f"Error reading drone file: {str(e)}"

class NodeDistanceTool(BaseTool):
    name: str = "Node Distance Tool"
    description: str = "Calculates shortest path between two nodes. Returns 'FAILURE' if distance > max_range. Inputs: start_node, end_node, max_range (optional)."
    
    # ¡AQUÍ ESTÁ LA MAGIA! Vinculamos el Schema explícito
    args_schema: Type[BaseModel] = NodeDistanceSchema

    # Ruta al mapa
    map_path: str = Field(default='src/mars_exploration/inputs/mars_terrain.graphml', description="Path to GraphML")

    def _run(self, start_node: str, end_node: str, max_range: float = None) -> str:
        try:
            # 1. Resolver ruta del mapa automáticamente igual que el JSON
            if not os.path.exists(self.map_path):
                base_path = os.path.dirname(os.path.abspath(__file__))
                self.map_path = os.path.join(base_path, '..', 'inputs', 'mars_terrain.graphml')
                self.map_path = os.path.normpath(self.map_path)

            if not os.path.exists(self.map_path):
                return f"Error: Map file not found at {self.map_path}"

            G = nx.read_graphml(self.map_path)
            
            if start_node not in G or end_node not in G:
                 return f"Error: Node {start_node} or {end_node} does not exist."

            try:
                distance = nx.shortest_path_length(G, source=start_node, target=end_node, weight='length')
            except nx.NetworkXNoPath:
                return "FAILURE: No path exists (unreachable)."

            # Validación de rango
            if max_range is not None:
                limit = float(max_range)
                if distance > limit:
                    return f"FAILURE: Target too far. Dist: {distance:.2f} > Range: {limit}. Pick closer target."
            
            path = nx.shortest_path(G, source=start_node, target=end_node, weight='length')
            return f"SUCCESS: Path: {path}, Total Distance: {distance:.2f}"

        except Exception as e:
            return f"Error calculating path: {str(e)}"