"""
Truth Maintenance System (TMS) for the propagation network.

This module implements support for tracking the premises that justify
values in the propagation network.
"""
from layers import LayeredDatum, base_layer_value, support_layer_value

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

def implies(v1, v2): #cant we just use a set comparison?
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
    s1_support = support_layer_value(s1)
    s2_support = support_layer_value(s2)
    return s1_support.is_subset(s2_support) and len(s1_support.premises) < len(s2_support.premises)

def merge_supports(support1, support2):
    """Merge two supports, combining their premises."""
    return support1.union(support2) 

# Helper functions for working with supports
def make_support(premises=None):
    """Create a new support with the given premises."""
    return Support(premises)

def supported(value, support):
    """Create a layered datum with the given value and support."""
    return LayeredDatum(value, support=support)

def supported_value(value, premises):
    """
    Create a value supported by a list of premises.
    
    Args:
        value: The base value
        premises: List of premises supporting the value
    
    Returns:
        A layered datum with the value and support
    """
    support = Support(premises)
    return supported(value, support)

###-----------------------------------LAYERED DATA HELPERS-----------------------------------###

def is_v_and_s(obj):
    """Check if an object is a value with support (layered datum with support layer)."""
    return isinstance(obj, LayeredDatum) and obj.has_layer('support')

def generic_flatten(layered_datum):
    """
    Flatten any nested layered data by merging their supports.
    """
    if not is_v_and_s(layered_datum):
        return layered_datum
    
    base_value = base_layer_value(layered_datum)
    support = support_layer_value(layered_datum)
    
    # If the base value is also a layered datum with support, combine them
    if is_v_and_s(base_value):
        inner_base = base_layer_value(base_value)
        inner_support = support_layer_value(base_value)
        combined_support = merge_supports(support, inner_support)
        return LayeredDatum(inner_base, support=combined_support)
    
    return layered_datum

###-----------------------------------TMS CLASS-----------------------------------###

class TMS:
    """
    A Truth Maintenance System (TMS) that contains a set of supported values.
    """
    
    def __init__(self, values=None):
        """
        Create a new TMS with an optional set of initial values.
        
        Args:
            values: Optional list of layered data objects with support.
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

def tms_query(value):
    """
    Get the most informative value supported by premises in the current worldview.
    
    If the value is a TMS, returns the strongest consequence while also
    updating the TMS to include this consequence if it improves the TMS.
    
    If the value is a layered datum with support, returns it if its support premises
    are all in the current worldview.
    
    Otherwise returns the value as is.
    """
    from nothing import NOTHING
    
    if isinstance(value, TMS):
        # Find the strongest consequence
        answer = strongest_consequence(value.values)
        
        # Assimilate that consequence back into the TMS
        better_tms = tms_assimilate(value.values, answer)
        
        # If the TMS has improved, update the original TMS
        if better_tms != value.values:
            value.values = better_tms
            
        return answer
    
    if is_v_and_s(value):
        # Get the support and check if all premises are in the current worldview
        support = support_layer_value(value)
        if all_premises_in(support.premises):
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
    # Extract base values
    v1 = base_layer_value(vs1)
    v2 = base_layer_value(vs2)
    
    # Extract supports
    s1 = support_layer_value(vs1)
    s2 = support_layer_value(vs2)
    
    # Check if v1 implies v2
    value_implies = implies(v1, v2)
    
    # Check if s1 is a subset of s2
    support_subset = s1.is_subset(s2)
    
    return value_implies and support_subset 

def tms_merge(tms1, tms2):
    """
    Merge two TMS values, assimilating facts and deducing consequences.
    """
    # First assimilate all values from tms2 into tms1
    candidate = tms_assimilate(tms1, tms2)
    
    # Then find the strongest consequence in the current worldview
    consequence = strongest_consequence(candidate)
    
    # Finally, assimilate this consequence back into the candidate
    return tms_assimilate(candidate, consequence)

def tms_assimilate(tms, stuff):
    """
    Incorporate values into a TMS without deducing consequences.
    """
    from nothing import NOTHING
    
    # Handle different types of input
    if stuff is NOTHING:
        return tms
    
    if is_v_and_s(stuff):
        return tms_assimilate_one(tms, stuff)
    
    if isinstance(stuff, list):  # A list of layered data values with support
        result = tms
        for item in stuff:
            result = tms_assimilate_one(result, item)
        return result
    
    # Default case
    return tms

def tms_assimilate_one(tms, v_and_s):
    """
    Add a single layered datum with support to a TMS, removing subsumed values.
    """
    # Check if any existing value subsumes the new one
    if any(subsumes(old_v_and_s, v_and_s) for old_v_and_s in tms):
        return tms
    
    # Find values that are subsumed by the new one
    subsumed = [old_v_and_s for old_v_and_s in tms if subsumes(v_and_s, old_v_and_s)]
    
    # Create a new TMS with the new value and without subsumed values
    return [v_and_s] + [old_v_and_s for old_v_and_s in tms if old_v_and_s not in subsumed]

def strongest_consequence(tms):
    """
    Find the most informative consequence of the current worldview.
    """
    from nothing import NOTHING
    from merge import merge
    
    # Filter for values that are believed in the current worldview
    relevant_values = []
    for v_and_s in tms:
        if is_v_and_s(v_and_s):
            support = support_layer_value(v_and_s)
            if all_premises_in(support.premises):
                relevant_values.append(v_and_s)
    
    # Merge all relevant values to find the strongest consequence
    result = NOTHING
    for v_and_s in relevant_values:
        result = merge(result, v_and_s)
    
    return result 