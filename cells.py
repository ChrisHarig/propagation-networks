from multipledispatch import dispatch

class Cell:
    """
    A cell stores partial information about a value and notifies neighbors when it changes.
    
    In propagation networks, cells are the repositories of values, and they are
    responsible for tracking the dependencies (interested propagators) and 
    triggering computation by alerting neighbors when they change.
    """
    
    def __init__(self, name=None): #should we use getters?
        self.name = name
        self.content = None  # Following the paper, this stores the cell's content
        self.neighbors = []  # Propagators that depend on this cell
    
    def new_neighbor(self, neighbor):
        """
        Register a new propagator as interested in this cell's value.
        The propagator will be notified when this cell's content changes.
        """
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            alert_propagator(neighbor)
        
    
    def add_content(self, content):
        """
        Add new content to this cell. If the content changes,
        alert the neighbors (propagators) that depend on this cell.
        
        This triggers the propagation of information through the network.
        
        Returns True if the content was updated, False otherwise.
        """
        # If we have no content yet, just store it
        if self.content is None:
            self.content = content
            # Alert neighbors about the new content - this triggers propagation
            alert_propagators(self.neighbors)
            return True
        
        # If the new content is the same as the current content, do nothing
        if self.content == content:
            return False
        
        # Otherwise, we have a contradiction
        raise ValueError(f"Contradiction: Cell {self.name} already has value {self.content}, "
                         f"but trying to add {content}")
    
    def __str__(self):
        return f"Cell({self.name}: {self.content})"


def make_cell(name=None):
    """
    Factory function to create a new cell.
    This follows the paper's pattern of having a simple factory function.
    """
    return Cell(name)


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
        alert_propagator(self) # intentionally redundant alert
    
    def alert(self):
        """
        When a cell changes, it alerts this propagator.
        This immediately runs the propagator's operation, which may
        update cells and trigger further propagation.
        """
        # Simply run the operation immediately - no queue needed
        self.operation(self.cells)
    
    def __str__(self):
        return f"Propagator({self.name}: {self.cells})"


def make_propagator(to_do, neighbors, name=None):
    """
    Factory function to create a new propagator.
    This follows the paper's pattern of having simple factory functions.
    
    Args:
        to_do: The operation function to run when the propagator is alerted
        neighbors: The cells this propagator interacts with
        name: Optional name for debugging
    """
    return Propagator(to_do, neighbors, name)


def alert_propagator(propagator): # could this be a function of a cell?
    """
    Alert a single propagator that a cell's content has changed.
    
    Args:
        propagator: The propagator to alert
    """
    propagator.alert()

def alert_propagators(propagators): # could this be a function of a cell?
    """
    Alert a list of propagators that a cell's content has changed.
    
    Args:
        propagators: List of propagators to alert
    """
    for propagator in propagators:
        alert_propagator(propagator)

# Double check this ---- may need to handle None's differently
def function_to_propagator_constructor(f):
    """
    Creates a propagator constructor from a regular function.
    
    This allows us to easily create propagators for operations like
    addition, subtraction, etc.
    
    Args:
        f: The function to convert into a propagator constructor
        
    Returns:
        A function that creates a propagator when given cells
    """
    def constructor(*cells):
        # The last cell is the output, the rest are inputs
        output = cells[-1]
        inputs = cells[:-1]
        
        # Create a propagator that watches the inputs but not the output
        def operation(cells):
            # Get the content of all input cells
            input_values = [cell.content for cell in inputs]
            
            # Only proceed if all inputs have values
            if all(val is not None for val in input_values):
                # Apply the function to the input values
                result = f(*input_values)
                # Add the result to the output cell
                output.add_content(result)
        
        # Create and return the propagator
        return make_propagator(operation, inputs)
    
    return constructor

# Example usage of function_to_propagator_constructor
def adder():
    """
    Creates a propagator that adds two values.
    
    Usage: adder()(a, b, c) creates a propagator that ensures c = a + b
    """
    return function_to_propagator_constructor(lambda x, y: x + y)

def subtractor():
    """
    Creates a propagator that subtracts one value from another.
    
    Usage: subtractor()(a, b, c) creates a propagator that ensures c = a - b
    """
    return function_to_propagator_constructor(lambda x, y: x - y)

def multiplier():
    """
    Creates a propagator that multiplies two values.
    
    Usage: multiplier()(a, b, c) creates a propagator that ensures c = a * b
    """
    return function_to_propagator_constructor(lambda x, y: x * y)

def divider():
    """
    Creates a propagator that divides one value by another.
    
    Usage: divider()(a, b, c) creates a propagator that ensures c = a / b
    """
    return function_to_propagator_constructor(lambda x, y: x / y)

# Example usage
if __name__ == "__main__":
    # Create cells
    a = make_cell("a")
    b = make_cell("b")
    c = make_cell("c")
    d = make_cell("d")
    e = make_cell("e")
    
    # Simple test of function-based propagators
    print("Testing function-based propagators:")
    
    # Create an adder propagator: c = a + b
    adder()(a, b, c)
    
    # Create a multiplier propagator: e = c * d
    multiplier()(c, d, e)
    
    # Set initial values
    a.add_content(3)
    b.add_content(4)
    d.add_content(2)
    
    # Print results
    print(f"a = {a.content}")  # Should be 3
    print(f"b = {b.content}")  # Should be 4
    print(f"c = {c.content}")  # Should be 7 (a + b)
    print(f"d = {d.content}")  # Should be 2
    print(f"e = {e.content}")  # Should be 14 (c * d = (a + b) * d)


