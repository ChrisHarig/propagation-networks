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
    
    def __init__(self, operation, cells, name=None):
        """
        Initialize a propagator.
        
        Args:
            operation: A function that operates on and updates cell values.
            cells: The cells this propagator interacts with.
            name: Optional name for debugging.
        """
        self.operation = operation
        self.cells = cells
        self.name = name
        
        # Register this propagator with all its cells
        for cell in cells:
            cell.new_neighbor(self)
    
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


def make_propagator(operation, cells, name=None):
    """
    Factory function to create a new propagator.
    This follows the paper's pattern of having simple factory functions.
    """
    return Propagator(operation, cells, name)


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


# Example usage
if __name__ == "__main__":
    # Create cells
    a = make_cell("a")
    b = make_cell("b")
    c = make_cell("c")
    d = make_cell("d")
    e = make_cell("e")
    

