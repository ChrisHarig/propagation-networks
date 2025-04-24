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
        
    def draw(self, filename=None):
        """Draw the current state of the network."""
        pos = nx.spring_layout(self.graph)
        
        # Draw cells
        cell_nodes = [n for n,d in self.graph.nodes(data=True) if d.get('type')=='cell']
        nx.draw_networkx_nodes(self.graph, pos, nodelist=cell_nodes, 
                             node_color='lightblue', node_shape='o', 
                             node_size=700, alpha=0.8)
        
        # Draw propagators
        prop_nodes = [n for n,d in self.graph.nodes(data=True) if d.get('type')=='propagator']
        nx.draw_networkx_nodes(self.graph, pos, nodelist=prop_nodes,
                             node_color='lightgreen', node_shape='s',
                             node_size=700, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, width=1.5, alpha=0.7)
        
        # Create labels with content for cells
        labels = {}
        for node, attrs in self.graph.nodes(data=True):
            if attrs.get('type') == 'cell':
                labels[node] = f"{node}: {attrs.get('content', '')}"
            else:
                labels[node] = node
                
        nx.draw_networkx_labels(self.graph, pos, labels=labels, font_size=10)
        
        plt.title("Propagator Network Visualization")
        plt.axis('off')
        
        # Save the figure if a filename is provided
        if filename:
            plt.savefig(f"{filename}.png", format="PNG", dpi=300, bbox_inches='tight')
            print(f"Network visualization saved to {filename}.png")
            
        plt.show() 