# src/mars_exploration/tools/graphTool.py
import networkx as nx
from crewai.tools import BaseTool
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field

class GraphMLInput(BaseModel):
    """Input for GraphMLReaderTool."""
    file_path: str = Field(
        ..., description="Path to the .graphml file containing the Mars map."
    )

class GraphMLReaderTool(BaseTool):
    name: str = "Mars Terrain Graph Reader"
    description: str = (
        "Loads and analyzes the topological map of Mars. "
        "Extracts information about nodes (coordinates, terrain type) "
        "and their connections (edges) for route planning."
    )
    args_schema: Type[BaseModel] = GraphMLInput

    def _run(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: Terrain file not found at {file_path}"

            # Load the graph using NetworkX
            G = nx.read_graphml(path)
            
            # 1. Extract Node information (terrain attributes)
            nodes_info = []
            for node, data in G.nodes(data=True):
                # Extract common attributes such as 'terrain', 'elevation', etc.
                terrain = data.get('terrain_type', 'unknown')
                nodes_info.append(f"Node {node}: Terrain={terrain}")

            # 2. Extract Edge information (available paths)
            edges_info = []
            for u, v, data in G.edges(data=True):
                distance = data.get('distance', 'N/A')
                edges_info.append(f"{u} <-> {v} (Distance: {distance})")

            # 3. Format output for the Agent
            summary = (
                f"--- Mars Map Summary ---\n"
                f"Total locations (Nodes): {G.number_of_nodes()}\n"
                f"Total routes (Edges): {G.number_of_edges()}\n\n"
                f"Terrain Details:\n" + "\n".join(nodes_info) + "\n\n"
                f"Network Connections:\n" + "\n".join(edges_info)
            )
            return summary

        except Exception as e:
            return f"Error processing the Mars graph: {str(e)}"
