from multipledispatch import dispatch

###----------------------------NOTHING OBJECT----------------------------###

class Nothing:
    """
    Represents the absence of information in a cell.
    
    This is distinct from None and allows us to explicitly handle
    the case where a cell has no information yet.
    """
    def __eq__(self, other):
        return isinstance(other, Nothing)
    
    def __str__(self):
        return "Nothing"

# Create a singleton instance
NOTHING = Nothing()

###----------------------------CELL OBJECT----------------------------###

class Cell:
    """
    A cell stores partial information about a value and notifies neighbors when it changes.
    
    In propagation networks, cells are the repositories of values, and they are
    responsible for tracking the dependencies (interested propagators) and 
    triggering computation by alerting neighbors when they change.
    """
    
    def __init__(self, name=None):
        self.name = name
        self._content = NOTHING  # Use NOTHING instead of None
        self._neighbors = []  # Propagators that depend on this cell - now private
    
    def new_neighbor(self, neighbor):
        """
        Register a new propagator as interested in this cell's value.
        The propagator will be notified when this cell's content changes.
        """
        if neighbor not in self._neighbors:
            self._neighbors.append(neighbor)
            alert_propagator(neighbor)
    
    def content(self):
        """
        Returns the current content of the cell.
        This follows the paper's pattern of having a content accessor.
        """
        return self._content
        
    def add_content(self, content): # may not need to return anything
        """
        Add new content to this cell according to the information regime:
        
        1. Adding NOTHING to a cell is always ok and doesn't change the content
        2. Adding a value to a cell with NOTHING sets the cell's content to that value
        3. Adding a value to a cell with the same value does nothing
        4. Adding a value to a cell with a different value signals an error
        
        Returns True if the content was updated, False otherwise.
        """
        # Case 1: Adding NOTHING is always ok and doesn't change anything
        if content is NOTHING:
            return False
        
        # Case 2: If we have no content yet, store the new content
        if self._content is NOTHING:
            self._content = content
            # Alert neighbors about the new content - this triggers propagation
            alert_propagators(self._neighbors)
            return True
        
        # Case 3: If the new content is the same as the current content, do nothing
        if self._content == content:
            return False
        
        # Case 4: Otherwise, we have a contradiction
        raise ValueError(f"Contradiction: Cell {self.name} already has value {self._content}, "
                         f"but trying to add {content}")
    
    def __str__(self):
        return f"Cell({self.name}: {self._content})"


def make_cell(name=None):
    """
    Factory function to create a new cell.
    This follows the paper's pattern of having a simple factory function.
    """
    return Cell(name)

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

###----------------------------FUNCTION TOPROPAGATOR CONSTRUCTOR----------------------------###


def function_to_propagator_constructor(f): #double check this, may need to handle None's differently
    #we should not just run the propagator in this fucntion, should just exist
    """
    Creates a propagator constructor from a regular function.
    Enhanced to handle NOTHING values explicitly.
    
    Args:
        f: The function to convert into a propagator constructor
        
    Returns:
        A function that creates a propagator when given cells
    """
    def constructor(*cells):
        output = cells[-1]
        inputs = cells[:-1]
        
        def operation(cells):
            # Get the content of all input cells
            input_values = [cell.content() for cell in inputs]
            
            # Check if any input is NOTHING
            if any(val is NOTHING for val in input_values):
                # Can't compute with missing information
                return
            
            try:
                # Apply the function to the input values
                result = f(*input_values)
                # Add the result to the output cell
                output.add_content(result)
            except Exception as e:
                # Handle computation errors (like division by zero)
                print(f"Computation error in {f.__name__ if hasattr(f, '__name__') else 'propagator'}: {e}")
        
        return make_propagator(operation, cells)  # Pass all cells to the propagator
    
    return constructor

###----------------------------PROPAGATOR CONSTRUCTOR EXAMPLES----------------------------###

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

###----------------------------MAIN USAGE EXAMPLE----------------------------###

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

    a.add_content(3)
    b.add_content(4)

    # Create an adder propagator: c = a + b
    adder()(a, b, c)

    # Create a multiplier propagator: e = c * d
    multiplier()(c, d, e)
    
    # Set initial values
    d.add_content(2)
    
    # Print results
    print(f"a = {a.content()}")  # Should be 3
    print(f"b = {b.content()}")  # Should be 4
    print(f"c = {c.content()}")  # Should be 7 (a + b)
    print(f"d = {d.content()}")  # Should be 2
    print(f"e = {e.content()}")  # Should be 14 (c * d = (a + b) * d)


