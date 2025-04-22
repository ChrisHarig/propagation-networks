from nothing import NOTHING

###----------------------------PROPAGATOR OBJECT----------------------------###
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


def make_propagator(to_do, neighbors, name=None): #can we just have prop constructor?
    """
    Factory function to create a new propagator.
    """
    return Propagator(to_do, neighbors, name)

def alert_propagator(propagator):
    """
    Alert a single propagator that a cell's content has changed.
    """
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