from nothing import NOTHING, THE_CONTRADICTION, contradictory
from propagator import alert_propagators
from multipledispatch import dispatch
from generic_operations import generic_merge
from tms import TMS
from layers import LayeredDatum, base_layer_value, support_layer_value

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
            increment: The new content to add to this cell.
        """
        from nothing import contradictory
        from generic_operations import generic_merge
        from layers import LayeredDatum
        
        # Ensure the increment is a LayeredDatum if it isn't already
        if not isinstance(increment, LayeredDatum):
            from layers import make_layered_datum
            increment = make_layered_datum(increment)
            
        # Merge the new content with existing content
        merged = generic_merge(self._content, increment)
        
        # Check for contradictions
        if contradictory(merged):
            raise ValueError(f"Contradiction in cell {self.name}: cannot merge {self._content} with {increment}")
        
        # Update content and alert propagators if changed
        if merged != self._content:
            self._content = merged
            self._alert_propagators()
    
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
    return Cell(name)