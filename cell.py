from nothing import NOTHING, contradictory
from propagator import alert_propagators

# Add global visualizer variable at the top of the file
_visualizer = None

def set_visualizer(visualizer):
    """Set the global visualizer for cells."""
    global _visualizer
    _visualizer = visualizer

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
        self._content = NOTHING  # Start with NOTHING
        self._neighbors = []  # Propagators that depend on this cell
    
    def new_neighbor(self, neighbor):
        """
        Register a new propagator as interested in this cell's value.
        The propagator will be notified when this cell's content changes.
        """
        if neighbor not in self._neighbors:
            self._neighbors.append(neighbor)
            # Remove NetworkTracker notification
            from propagator import alert_propagator  # Import here to avoid circular imports
            alert_propagator(neighbor)
    
    def content(self):
        """
        Returns the current content of the cell.
        """
        return self._content
        
    def add_content(self, increment):
        """
        Add new content to this cell using the generic merge system.
        
        Args:
            increment: New information to add to this cell
            
        Returns:
            True if the cell's content changed, False otherwise
            
        Raises:
            ValueError: If the new information contradicts existing information
        """
        old_content = self._content
        # Use the generic merge function to combine information
        new_content = merge(self._content, increment)
        
        # Check for contradictions
        if contradictory(new_content):
            raise ValueError(f"Contradiction in Cell {self.name}: "
                            f"Cannot merge {self._content} with {increment}")
        
        # If the content didn't change (by identity), no need to alert neighbors
        if new_content is self._content:
            return False
            
        # Update content and alert neighbors
        self._content = new_content
        
        if _visualizer:
            _visualizer.on_cell_updated(self, old_content, new_content)
        
        alert_propagators(self._neighbors)
        return True
    
    def __str__(self):
        return f"Cell({self.name}: {self._content})"


def make_cell(name=None):
    """
    Factory function to create a new cell.
    This follows the paper's pattern of having a simple factory function.
    """
    cell = Cell(name)
    if _visualizer:
        _visualizer.on_cell_created(cell)
    return cell 

###----------------------------MERGE LOGIC----------------------------###

def merge(content, increment):
    """
    Generic merge function for combining partial information.
    
    This is the main extension point for different types of partial information.
    The contract is:
    - If increment adds no new information, return content exactly (by identity)
    - If increment contradicts content, return THE_CONTRADICTION
    - If increment supersedes content, return increment exactly
    - Otherwise, return a new merged value
    
    Args:
        content: Current information
        increment: New information to merge
        
    Returns:
        Merged information, or THE_CONTRADICTION if they're inconsistent
    """
    from interval import Interval, to_interval  # Import here to avoid circular imports
    from nothing import THE_CONTRADICTION
    
    if content is NOTHING or increment is NOTHING:
        return increment if content is NOTHING else content
    
    # Case 2: Two intervals - intersect them
    if isinstance(content, Interval) and isinstance(increment, Interval):
        new_interval = Interval.intersect(content, increment)
        if new_interval.is_empty():
            return THE_CONTRADICTION
        
        # Check if the result is exactly one of the inputs
        # (using a small tolerance for floating point comparisons)
        tolerance = 1e-9
        if (abs(new_interval.low - content.low) < tolerance and 
            abs(new_interval.high - content.high) < tolerance):
            return content
        if (abs(new_interval.low - increment.low) < tolerance and 
            abs(new_interval.high - increment.high) < tolerance):
            return increment
        
        return new_interval
    
    # Case 3: Interval merged with a number - check if number is in interval
    if isinstance(content, Interval) and isinstance(increment, (int, float)):
        if content.low <= increment <= content.high:
            # The number is consistent with the interval
            # Since the number is more specific, return it
            return increment
        else:
            # The number is outside the interval - contradiction
            return THE_CONTRADICTION
    
    # Case 4: Number merged with an interval - check if number is in interval
    if isinstance(content, (int, float)) and isinstance(increment, Interval):
        if increment.low <= content <= increment.high:
            # The number is consistent with the interval
            # Since the number is more specific, return it
            return content
        else:
            # The number is outside the interval - contradiction
            return THE_CONTRADICTION
    
    # Case 5: Two raw values - they must be equal
    if content == increment:
        return content
    else:
        return THE_CONTRADICTION