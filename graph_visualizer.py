import networkx as nx
import matplotlib.pyplot as plt

class GraphVisualizer:
    def __init__(self):
        self.graph = nx.Graph()
        
    def on_cell_created(self, cell):
        """Called when a cell is created."""
        self.graph.add_node(cell.name or str(id(cell)), 
                          type='cell',
                          content=str(cell.content()))
        
    def on_propagator_created(self, propagator):
        """Called when a propagator is created."""
        self.graph.add_node(propagator.name or str(id(propagator)),
                          type='propagator')
        
    def on_cell_updated(self, cell, old_value, new_value):
        """Called when a cell's value changes."""
        node_id = cell.name or str(id(cell))
        self.graph.nodes[node_id]['content'] = str(new_value)
        
    def on_connection_made(self, propagator, cell):
        """Called when a propagator connects to a cell."""
        prop_id = propagator.name or str(id(propagator))
        cell_id = cell.name or str(id(cell))
        self.graph.add_edge(prop_id, cell_id)
        
    def draw(self, title=None, simplify_values=False):
        """
        Draw the current network graph.
        
        Args:
            title: Optional title for the graph
            simplify_values: If True, attempt to extract and display only the core value
                             when cell content is a complex object
        """
        plt.figure(figsize=(12, 8))
        
        # Create position layout
        pos = nx.spring_layout(self.graph)
        
        # Draw cells (blue)
        cell_nodes = [n for n, attr in self.graph.nodes(data=True) 
                     if attr.get('type') == 'cell']
        nx.draw_networkx_nodes(self.graph, pos, nodelist=cell_nodes, 
                              node_color='skyblue', node_size=700)
        
        # Draw propagators (red)
        prop_nodes = [n for n, attr in self.graph.nodes(data=True) 
                     if attr.get('type') == 'propagator']
        nx.draw_networkx_nodes(self.graph, pos, nodelist=prop_nodes, 
                              node_color='salmon', node_size=500)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos)
        
        # Draw labels - simplify values if requested
        cell_labels = {}
        for n in cell_nodes:
            content = self.graph.nodes[n].get('content', '')
            if simplify_values and hasattr(content, 'value'):
                # For complex objects that have a 'value' attribute
                try:
                    # Try to access the value attribute
                    display_content = str(content.value)
                except:
                    # Fall back to the full string representation
                    display_content = str(content)
            else:
                display_content = str(content)
            
            cell_labels[n] = f"{n}\n{display_content}"
        
        nx.draw_networkx_labels(self.graph, pos, labels=cell_labels)
        
        prop_labels = {n: n for n in prop_nodes}
        nx.draw_networkx_labels(self.graph, pos, labels=prop_labels)
        
        # Set title if provided
        if title:
            plt.title(title)
        else:
            plt.title("Propagation Network")
            
        plt.axis('off')
        plt.tight_layout()
        plt.show() 