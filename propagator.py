from nothing import NOTHING

# Global registry of propagators that have ever been alerted
# Using a dictionary as Python's equivalent of a hash table
_propagators_ever_alerted = {}
_propagators_ever_alerted_list = []

class Propagator:
    """
    A propagator enforces a relationship between cells.
    
    When alerted (by a cell whose value has changed), the propagator
    immediately runs its operation, which may update other cells and 
    trigger further propagation naturally.
    """
    
    def __init__(self, to_do, neighbors, name=None):
        """
        Initialize a propagator.
        
        Args:
            to_do: A function that operates on and updates cell values.
            neighbors: The cells this propagator interacts with.
            name: Optional name for debugging.
        """
        self.operation = to_do
        self.cells = neighbors
        self.name = name
        
        # Register this propagator with all its cells
        for cell in neighbors:
            cell.new_neighbor(self)
            
        # Alert the propagator at least once during initialization
        alert_propagator(self)
    
    def alert(self):
        """
        When a cell changes, it alerts this propagator.
        This immediately runs the propagator's operation, which may
        update cells and trigger further propagation.
        """
        try:
            self.operation()
        except ValueError as e:
            # Catch contradiction errors during propagation
            print(f"Contradiction detected by {self.name or 'Unnamed Propagator'}: {e}")
    
    def __str__(self):
        cell_names = ', '.join(c.name or '?' for c in self.cells)
        return f"Propagator({self.name or 'Unnamed'}: [{cell_names}])"

def make_propagator(to_do, neighbors, name=None):
    """Factory function to create a new propagator."""
    return Propagator(to_do, neighbors, name)

def register_alerted_propagator(propagator):
    """
    Register a propagator as having been alerted.
    This follows the paper's implementation of tracking propagators
    that have ever been alerted.
    """
    global _propagators_ever_alerted, _propagators_ever_alerted_list
    
    # Only add to the registry if it's not already there
    if propagator not in _propagators_ever_alerted:
        _propagators_ever_alerted[propagator] = True
        _propagators_ever_alerted_list.append(propagator)

def alert_propagator(propagator):
    """
    Alert a single propagator that a cell's content has changed.
    """
    # Register this propagator as having been alerted
    register_alerted_propagator(propagator)
    
    # Run the propagator
    propagator.alert()

def alert_propagators(propagators):
    """
    Alert a list of propagators that a cell's content has changed.
    """
    for propagator in propagators:
        alert_propagator(propagator)

def function_to_propagator_constructor(f):
    """
    Creates a propagator constructor from a regular function.
    
    Args:
        f: The function to convert into a propagator constructor
        
    Returns:
        A function that creates a propagator when given cells
    """
    def constructor(*cells):
        output = cells[-1]
        inputs = cells[:-1]
        
        def operation(): 
            # Get the content of all input cells
            input_values = [cell.content() for cell in inputs]
            
            # Apply the function to the input values
            # The function should handle partial information itself
            result = f(*input_values)
            
            # Add the result to the output cell if it's not NOTHING
            if result is not NOTHING:
                output.add_content(result)
        
        return make_propagator(operation, cells, name=f.__name__ if hasattr(f, '__name__') else None)
    
    return constructor 

def alert_all_propagators():
    """
    Alert all propagators in the system.
    
    This is used when the worldview changes to ensure all
    propagators get a chance to recompute based on the new worldview.
    """
    global _propagators_ever_alerted_list
    
    if not _propagators_ever_alerted_list:
        print("Warning: No propagators have been alerted yet.")
        return
        
    print(f"Alerting all {len(_propagators_ever_alerted_list)} registered propagators...")
    for propagator in _propagators_ever_alerted_list:
        propagator.alert()  # Direct call to alert to avoid re-registration 