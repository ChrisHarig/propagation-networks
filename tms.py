"""
Truth Maintenance System (TMS) for the propagation network.

This module implements support for tracking the premises that justify
values in the propagation network.
"""


###-----------------------------------GLOBAL WORLDVIEW-----------------------------------###

_current_worldview = set()

def premise_in(premise):
    """Check if a premise is in the current worldview."""
    if isinstance(premise, str):
        # Handle premises specified by name
        for p in _current_worldview:
            if hasattr(p, 'name') and p.name == premise:
                return True
        return False
    return premise in _current_worldview

def all_premises_in(premise_list):
    """Check if all premises in the list are in the current worldview."""
    return all(premise_in(p) for p in premise_list)

def kick_out(premise):
    """Remove a premise from the current worldview."""
    global _current_worldview
    
    # If the premise is a string, find the actual premise with that name
    if isinstance(premise, str):
        for p in list(_current_worldview):
            if hasattr(p, 'name') and p.name == premise:
                _current_worldview.remove(p)
                from propagator import alert_all_propagators
                alert_all_propagators()
                return
    elif premise in _current_worldview:
        _current_worldview.remove(premise)
        from propagator import alert_all_propagators
        alert_all_propagators()

def bring_in(premise):
    """Add a premise to the current worldview."""
    global _current_worldview
    
    from propagator import alert_all_propagators
    # If the premise is already in, do nothing
    if premise_in(premise):
        return
    else:
        _current_worldview.add(premise)
        from propagator import alert_all_propagators
        alert_all_propagators()

# Initialize premise to be believed by default (no alert)
def initialize_premise(premise):
    """Initialize a premise as believed by default."""
    global _current_worldview
    _current_worldview.add(premise)
    return premise

###-----------------------------------PREMISE CLASS-----------------------------------###
class Premise:
    """A premise is a fundamental assumption that can support a value."""
    
    _next_id = 0
    
    def __init__(self, name=None):
        """
        Create a new premise with an optional name.
        
        Args:
            name: Optional name for the premise for debugging purposes.
        """
        self.id = Premise._next_id
        Premise._next_id += 1
        self.name = name or f"premise-{self.id}"
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Premise({self.name})"
    
# Factory function for making premises that are believed by default (no alert)
def make_premise(name=None):
    """Factory function to create a new premise that is believed by default."""
    premise = Premise(name)
    return initialize_premise(premise) # do we want to believe a premise by default?

###-----------------------------------SUPPORT CLASS-----------------------------------###
class Support:
    """
    A set of premises that together justify a value.
    """
    
    def __init__(self, premises=None):
        """
        Create a support with an optional set of initial premises.
        
        Args:
            premises: Optional set of premises.
        """
        self.premises = set(premises) if premises else set()
    
    def add(self, premise):
        """Add a premise to this support."""
        self.premises.add(premise)
    
    def union(self, other):
        """Create a new support that combines the premises of this and another support."""
        return Support(self.premises.union(other.premises))
    
    def is_subset(self, other):
        """Check if this support is a subset of another support."""
        return self.premises.issubset(other.premises)
    
    def __str__(self):
        if not self.premises:
            return "{}"
        return "{" + ", ".join(str(p) for p in self.premises) + "}"
    
    def __repr__(self):
        return f"Support({repr(self.premises)})"


def implies(v1, v2):
    """
    Check if v1 implies v2 (v1 is more specific than or equal to v2).
    
    This is true if v1 merged with v2 equals v2.
    """
    from merge import merge
    return merge(v1, v2) == v2


def more_informative_support(s1, s2):
    """
    Check if s1 has more informative support than s2.
    
    More informative support means it depends on fewer premises.
    """
    return s1.support.is_subset(s2.support) and len(s1.support.premises) < len(s2.support.premises)

def merge_supports(support1, support2):
    """Merge two supports, combining their premises."""
    return support1.union(support2) 

###-----------------------------------TMS CLASS-----------------------------------###

class TMS:
    """
    A Truth Maintenance System (TMS) that contains a set of supported values.
    
    This is the Python equivalent of the TMS record structure in the dissertation.
    """
    
    def __init__(self, values=None):
        """
        Create a new TMS with an optional set of initial values.
        
        Args:
            values: Optional list of ValueWithSupport objects.
        """
        self.values = values or []
    
    def __str__(self):
        if not self.values:
            return "TMS([])"
        return "TMS([" + ", ".join(str(v) for v in self.values) + "])"
    
    def __repr__(self):
        return f"TMS({repr(self.values)})"

def make_tms(values=None):
    """Factory function to create a new TMS."""
    return TMS(values) 

def tms_query(value): #edit to support layered data
    """
    Get the most informative value supported by premises in the current worldview.
    
    If the value is a TMS, returns the strongest consequence.
    If the value is a ValueWithSupport, returns it if its support premises
    are all in the current worldview.
    Otherwise returns the value as is.
    """
    from nothing import NOTHING
    
    if isinstance(value, TMS):
        return strongest_consequence(value.values)
    
    if is_v_and_s(value):
        # Check if the support premises are all in the current worldview
        if all_premises_in(value.support.premises):
            return value
        return NOTHING
    
    # For regular values, just return them
    return value

def subsumes(vs1, vs2):
    """
    Check if vs1 subsumes vs2 (the information in vs2 is deducible from vs1).
    
    This is true if:
    1. The value of vs1 implies the value of vs2
    2. The support of vs1 is a subset of the support of vs2
    """
    from merge import merge
    
    # Check if the value of vs1 implies the value of vs2
    value_implies = implies(vs1.value, vs2.value)
    
    # Check if the support of vs1 is a subset of the support of vs2
    support_subset = vs1.support.is_subset(vs2.support)
    
    return value_implies and support_subset 

def tms_merge(tms1, tms2):
    """
    Merge two TMS values, assimilating facts and deducing consequences.
    
    This is the Python equivalent of tms-merge from the dissertation.
    """
    # First assimilate all values from tms2 into tms1
    candidate = tms_assimilate(tms1, tms2)
    
    # Then find the strongest consequence in the current worldview
    consequence = strongest_consequence(candidate)
    
    # Finally, assimilate this consequence back into the candidate
    return tms_assimilate(candidate, consequence)

def tms_assimilate(tms, stuff): #edit to support layered data
    """
    Incorporate values into a TMS without deducing consequences.
    
    This is the Python equivalent of tms-assimilate from the dissertation.
    """
    from nothing import NOTHING
    
    # Handle different types of input
    if stuff is NOTHING:
        return tms
    
    if is_v_and_s(stuff):
        return tms_assimilate_one(tms, stuff)
    
    if isinstance(stuff, list):  # Assuming a list of v&s values
        result = tms
        for item in stuff:
            result = tms_assimilate_one(result, item)
        return result
    
    # Default case
    return tms

def tms_assimilate_one(tms, v_and_s): #edit to support layered data
    """
    Add a single ValueWithSupport to a TMS, removing subsumed values.
    
    This is the Python equivalent of tms-assimilate-one from the dissertation.
    """
    # Check if any existing value subsumes the new one
    if any(subsumes(old_v_and_s, v_and_s) for old_v_and_s in tms):
        return tms
    
    # Find values that are subsumed by the new one
    subsumed = [old_v_and_s for old_v_and_s in tms if subsumes(v_and_s, old_v_and_s)]
    
    # Create a new TMS with the new value and without subsumed values
    return [v_and_s] + [old_v_and_s for old_v_and_s in tms if old_v_and_s not in subsumed]

def strongest_consequence(tms): #edit to support layered data
    """
    Find the most informative consequence of the current worldview.
    
    This is the Python equivalent of strongest-consequence from the dissertation.
    """
    from nothing import NOTHING
    from merge import merge
    
    # Filter for values that are believed in the current worldview
    relevant_values = [v_and_s for v_and_s in tms if all_premises_in(v_and_s.support.premises)]
    
    # Merge all relevant values to find the strongest consequence
    result = NOTHING
    for v_and_s in relevant_values:
        result = merge(result, v_and_s)
    
    return result 