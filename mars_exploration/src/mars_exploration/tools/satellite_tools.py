import json
import os
import networkx as nx
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# --- 1. Schema para SatelliteLinkTool ---
class SatelliteLinkSchema(BaseModel):
    """Input schema for SatelliteLinkTool."""
    start_node: str = Field(..., description="The origin satellite or ground node ID (e.g., 'S1').")
    end_node: str = Field(..., description="The destination satellite or ground node ID (e.g., 'S52').")
    max_communication_range: Optional[float] = Field(
        None,
        description="Maximum communication range of the satellite. If provided, fails when distance exceeds it."
    )

# --- 2. Satellite Info Tool ---
class SatelliteInfoTool(BaseTool):
    name: str = "Satellite Info Reader"
    description: str = (
        "Reads the technical specifications of the satellite network. "
        "Returns orbital and communication capabilities. No input required."
    )

    def _run(self, file_path: str = None) -> str:
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_path, '..', 'inputs', 'satellites.json')
            json_path = os.path.normpath(json_path)

            if not os.path.exists(json_path):
                return f"Error: Satellite configuration file not found at {json_path}"

            with open(json_path, 'r') as f:
                data = json.load(f)

            return json.dumps(data, indent=2)

        except Exception as e:
            return f"Error reading satellite file: {str(e)}"

# --- 3. Satellite Link Tool ---
class SatelliteLinkTool(BaseTool):
    name: str = "Satellite Link Distance Tool"
    description: str = (
        "Calculates the shortest communication path between two satellites or nodes. "
        "Returns FAILURE if the distance exceeds the satellite communication range."
    )

    args_schema: Type[BaseModel] = SatelliteLinkSchema

    map_path: str = Field(
        default='src/mars_exploration/inputs/mars_terrain.graphml',
        description="GraphML file representing satellite and relay network."
    )

    def _run(
        self,
        start_node: str,
        end_node: str,
        max_communication_range: float = None
    ) -> str:
        try:
            if not os.path.exists(self.map_path):
                base_path = os.path.dirname(os.path.abspath(__file__))
                self.map_path = os.path.join(base_path, '..', 'inputs', 'mars_terrain.graphml')
                self.map_path = os.path.normpath(self.map_path)

            if not os.path.exists(self.map_path):
                return f"Error: Network map not found at {self.map_path}"

            G = nx.read_graphml(self.map_path)

            if start_node not in G or end_node not in G:
                return f"Error: Node {start_node} or {end_node} does not exist in the network."

            try:
                distance = nx.shortest_path_length(
                    G,
                    source=start_node,
                    target=end_node,
                    weight='length'
                )
            except nx.NetworkXNoPath:
                return "FAILURE: No communication path available."

            if max_communication_range is not None:
                limit = float(max_communication_range)
                if distance > limit:
                    return (
                        f"FAILURE: Communication range exceeded. "
                        f"Dist: {distance:.2f} > Range: {limit}"
                    )

            path = nx.shortest_path(
                G,
                source=start_node,
                target=end_node,
                weight='length'
            )

            return f"SUCCESS: Link Path: {path}, Total Distance: {distance:.2f}"

        except Exception as e:
            return f"Error calculating satellite link: {str(e)}"
