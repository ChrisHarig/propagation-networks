from nothing import NOTHING, THE_CONTRADICTION, contradictory
from propagator import alert_propagators
from multipledispatch import dispatch

# Add global visualizer variable at the top of the file
_visualizer = None

def set_visualizer(visualizer):
    """Set the global visualizer for cells."""
    global _visualizer
    _visualizer = visualizer

###----------------------------CELL OBJECT----------------------------###

class Cell:
    """
    A cell holds values which can represent partial information.
    
    Cells connect to propagators which can read and update their values
    in response to changes.
    """
    
    def __init__(self, name=None):
        """
        Initialize a cell with optional debugging name.
        
        Args:
            name: Optional name for debugging purposes.
        """
        self.name = name
        self._content = NOTHING
        self._neighbors = []  # List of propagators connected to this cell
    
    def content(self):
        """Get the current content of the cell."""
        return self._content
    
    def add_content(self, increment):
        """
        Add new content to this cell, merging with existing content.
        
        Args:
            increment: New information to be added to the cell.
            
        Raises:
            ValueError: If the new content contradicts existing content.
        """
        # If we have nothing, just set the content directly
        old_value = self._content
        
        if old_value is NOTHING:
            self._content = increment
            self._alert_propagators()
            # Notify visualizer if available
            if _visualizer and increment is not NOTHING:
                _visualizer.on_cell_updated(self, old_value, increment)
            return
        
        # Otherwise, we need to merge the new content with the existing content
        from generic_operations import generic_merge
        merged = generic_merge(old_value, increment)
        
        # Check for contradictions
        if contradictory(merged):
            raise ValueError(f"Contradiction in cell {self.name or 'unnamed'}: " +
                          f"Cannot merge {old_value} with {increment}")
        
        # If nothing changed, we're done
        if merged == old_value:
            return
        
        # Otherwise, update the content and alert propagators
        self._content = merged
        self._alert_propagators()
        
        # Notify visualizer if available
        if _visualizer:
            _visualizer.on_cell_updated(self, old_value, merged)
    
    def new_neighbor(self, propagator):
        """Add a propagator as a neighbor of this cell."""
        if propagator not in self._neighbors:
            self._neighbors.append(propagator)
    
    def _alert_propagators(self):
        """Alert all neighboring propagators that this cell has changed."""
        from propagator import alert_propagators
        alert_propagators(self._neighbors)
    
    def __str__(self):
        content_str = str(self._content) if self._content is not NOTHING else "NOTHING"
        return f"Cell({self.name or 'unnamed'}: {content_str})"

def make_cell(name=None):
    """Factory function to create a new cell."""
    cell = Cell(name)
    if _visualizer:
        _visualizer.on_cell_created(cell)
    return cell

###----------------------------MERGE LOGIC----------------------------###

# Base merge function that delegates to the appropriate implementation
def merge(content, increment):
    """
    Generic merge function for combining partial information.
    
    This is the main extension point for different types of partial information.
    The contract is:
    - If increment adds no new information, return content exactly (by identity)
    - If increment contradicts content, return THE_CONTRADICTION
    - If increment supersedes content, return increment exactly
    - Otherwise, return a new merged value
    """
    # Special case for NOTHING - handle outside of dispatch system
    if content is NOTHING or increment is NOTHING:
        return increment if content is NOTHING else content
    
    # Use the dispatch system for other cases
    return _merge_dispatch(content, increment)

# Multiple dispatch implementations for different type combinations
@dispatch(object, object)
def _merge_dispatch(content, increment):
    """Default implementation for types without a specific handler."""
    if content == increment:
        return content
    else:
        return THE_CONTRADICTION

@dispatch('Interval', 'Interval')
def _merge_dispatch(content, increment):
    """Merge two intervals by finding their intersection."""
    from interval import Interval
    
    # Use the intersection of the two intervals
    new_interval = Interval.intersect(content, increment)
    if new_interval.is_empty():
        return THE_CONTRADICTION
    
    # Check if the result is exactly one of the inputs
    tolerance = 1e-9
    if (abs(new_interval.low - content.low) < tolerance and 
        abs(new_interval.high - content.high) < tolerance):
        return content
    if (abs(new_interval.low - increment.low) < tolerance and 
        abs(new_interval.high - increment.high) < tolerance):
        return increment
    
    return new_interval

@dispatch('Interval', (int, float))
def _merge_dispatch(content, increment):
    """Merge an interval with a number."""
    if content.low <= increment <= content.high:
        # The number is consistent with the interval
        return increment
    else:
        # The number is outside the interval - contradiction
        return THE_CONTRADICTION

@dispatch((int, float), 'Interval')
def _merge_dispatch(content, increment):
    """Merge a number with an interval."""
    if increment.low <= content <= increment.high:
        # The number is consistent with the interval
        return content
    else:
        # The number is outside the interval - contradiction
        return THE_CONTRADICTION