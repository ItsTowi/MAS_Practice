import networkx as nx
from crewai_tools import BaseTool
from pydantic import Field

class NodeDistanceTool(BaseTool):
    name: str = "Node Distance Tool"
    description: str = "Calculates the shortest path based on DISTANCE between two nodes. Returns the path sequence and total length. Input: start_node, end_node."

    # Define la ruta al archivo por defecto
    map_path: str = Field(default='inputs/mars_terrain.graphml', description="Path to the GraphML file")

    def _run(self, start_node: str, end_node: str) -> str:
        try:
            # 1. Cargar el Grafo
            G = nx.read_graphml(self.map_path)
            
            # 2. Validar que los nodos existen
            if start_node not in G or end_node not in G:
                return f"Error: Node {start_node} or {end_node} does not exist."

            # 3. Calcular la ruta más corta usando 'length' como peso
            path = nx.shortest_path(G, source=start_node, target=end_node, weight='length')
            
            # 4. Calcular la distancia total exacta
            total_distance = nx.shortest_path_length(G, source=start_node, target=end_node, weight='length')
            
            # Redondeamos para que el LLM no procese numeros con muchos decimales
            total_distance = round(total_distance, 2)

            return f"Path: {path}, Total Distance: {total_distance}"
        
        except nx.NetworkXNoPath:
            return "Error: No path exists between these locations (unreachable)."
        except KeyError:
            # Si el grafo no tiene el atributo 'length' definido
            return "Error: The map edges do not have a 'length' attribute."
        except Exception as e:
            return f"Navigation Error: {str(e)}"