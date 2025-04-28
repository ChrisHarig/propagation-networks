from nothing import NOTHING, THE_CONTRADICTION, contradictory
from propagator import alert_propagators
from multipledispatch import dispatch
from merge import merge
from tms import is_v_and_s, ValueWithSupport, TMS

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
            increment: The new content to add to this cell.
        """
        from nothing import NOTHING, contradictory
        from merge import merge
        from tms import TMS, is_v_and_s
        
        # Nothing is a no-op
        if increment is NOTHING:
            return
        
        # Handle TMS values specially
        if isinstance(increment, TMS) or isinstance(self._content, TMS):
            merged = merge(self._content, increment)
            
            # Check for contradictions
            if contradictory(merged):
                raise ValueError(f"Contradiction in cell {self.name}: cannot merge {self._content} with {increment}")
            
            # Update content and alert propagators if changed
            if merged != self._content:
                old_content = self._content
                self._content = merged
                if _visualizer:
                    _visualizer.on_cell_updated(self, old_content, merged)
                self._alert_propagators()
            return
        
        # Handle ValueWithSupport values
        if is_v_and_s(increment) or is_v_and_s(self._content):
            merged = merge(self._content, increment)
            
            # Check for contradictions
            if contradictory(merged):
                raise ValueError(f"Contradiction in cell {self.name}: cannot merge {self._content} with {increment}")
            
            # Update content and alert propagators if changed
            if merged != self._content:
                old_content = self._content
                self._content = merged
                if _visualizer:
                    _visualizer.on_cell_updated(self, old_content, merged)
                self._alert_propagators()
            return
        
        # Regular case (non-TMS, non-ValueWithSupport)
        merged = merge(self._content, increment)
        
        # Check for contradictions
        if contradictory(merged):
            raise ValueError(f"Contradiction in cell {self.name}: cannot merge {self._content} with {increment}")
        
        # Update content and alert propagators if changed
        if merged != self._content:
            old_content = self._content
            self._content = merged
            if _visualizer:
                _visualizer.on_cell_updated(self, old_content, merged)
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
    cell = Cell(name)
    if _visualizer:
        _visualizer.on_cell_created(cell)
    return cell