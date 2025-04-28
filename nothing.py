"""
Defines concepts of nothingness and contradiction for the propagation network.
"""

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

# Unique object to represent contradictions
THE_CONTRADICTION = object()  

def contradictory(thing):
    """
    Generic function to check if something represents a contradiction.
    
    Uses duck typing to check for contradictions (either is THE_CONTRADICTION
    or has an is_empty method that returns True).
    """
    if thing is THE_CONTRADICTION:
        return True
    
    # Use duck typing instead of explicit type checking
    if hasattr(thing, 'is_empty') and callable(thing.is_empty):
        return thing.is_empty()
    
    return False 