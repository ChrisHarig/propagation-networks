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
    
    Currently only checks for THE_CONTRADICTION sentinel, but can be
    extended for other types that might represent contradictions.
    """
    from interval import Interval  # Import here to avoid circular imports
    
    return thing is THE_CONTRADICTION or (
        isinstance(thing, Interval) and thing.is_empty()) 