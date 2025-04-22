import math
from nothing import NOTHING, THE_CONTRADICTION

###----------------------------INTERVAL CLASS----------------------------###

class Interval: 
    """Represents a closed interval [low, high]."""
    def __init__(self, low, high):
        if low > high:
            # Represent an empty interval (contradiction)
            # Using NaN allows easy detection of empty intervals
            self.low = float('nan') #probably should make an empty object
            self.high = float('nan')
        else:
            self.low = low
            self.high = high

    def is_empty(self):
        """Check if the interval is empty (represents a contradiction)."""
        return math.isnan(self.low) or math.isnan(self.high)

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        if self.is_empty() and other.is_empty():
            return True
        return self.low == other.low and self.high == other.high

    def __str__(self):
        if self.is_empty():
            return "Interval(Empty)"
        return f"Interval([{self.low}, {self.high}])"

    def __repr__(self):
        return str(self)

    @staticmethod
    def intersect(i1, i2):
        """Computes the intersection of two intervals."""
        if i1.is_empty() or i2.is_empty():
            return Interval(float('nan'), float('nan')) # Intersection with empty is empty
        low = max(i1.low, i2.low)
        high = min(i1.high, i2.high)
        return Interval(low, high)

    @staticmethod
    def union(i1, i2):
         """Computes the union of two intervals (smallest interval containing both)."""
         # Note: This is not the set-theoretic union if intervals are disjoint
         if i1.is_empty():
             return i2
         if i2.is_empty():
             return i1
         low = min(i1.low, i2.low)
         high = max(i1.high, i2.high)
         return Interval(low, high)

# Define interval constants
EMPTY_INTERVAL = Interval(float('nan'), float('nan')) # Represents contradiction

def to_interval(value):
    """Converts a number to an Interval object with equal bounds."""
    if isinstance(value, Interval):
        return value
    elif isinstance(value, (int, float)):
        # Convert number to a point interval
        return Interval(float(value), float(value))
    else:
        raise TypeError(f"Cannot convert {type(value)} to Interval")

###----------------------------INTERVAL ARITHMETIC----------------------------###

def add_intervals(i1, i2):
    """Interval addition: [a,b] + [c,d] = [a+c, b+d]"""
    if i1.is_empty() or i2.is_empty(): 
        return EMPTY_INTERVAL
    return Interval(i1.low + i2.low, i1.high + i2.high)

def sub_intervals(i1, i2):
    """Interval subtraction: [a,b] - [c,d] = [a-d, b-c]"""
    if i1.is_empty() or i2.is_empty(): 
        return EMPTY_INTERVAL
    return Interval(i1.low - i2.high, i1.high - i2.low)

def mul_intervals(i1, i2):
    """Interval multiplication: [a,b] * [c,d]"""
    if i1.is_empty() or i2.is_empty(): 
        return EMPTY_INTERVAL
    # Compute the 4 endpoint products
    p1 = i1.low * i2.low
    p2 = i1.low * i2.high
    p3 = i1.high * i2.low
    p4 = i1.high * i2.high
    # The result is the interval [min(p1..p4), max(p1..p4)]
    return Interval(min(p1, p2, p3, p4), max(p1, p2, p3, p4))

def div_intervals(i1, i2):
    """Interval division: [a,b] / [c,d]"""
    if i1.is_empty() or i2.is_empty(): 
        return EMPTY_INTERVAL
    # Check if the divisor interval contains zero
    if i2.low <= 0 <= i2.high:
        # Division by zero is possible.
        if i2.low == 0 and i2.high == 0:
            print(f"Warning: Division by zero interval {i2} attempted.")
            return EMPTY_INTERVAL
        print(f"Warning: Division by interval {i2} containing zero.")
        # For simplicity, we'll return a very wide interval
        return Interval(-float('inf'), float('inf'))

    # If no division by zero, compute 1/[c,d] = [1/d, 1/c]
    # Note the swap because 1/x is decreasing
    reciprocal_i2 = Interval(1.0 / i2.high, 1.0 / i2.low)
    # Then multiply i1 by the reciprocal interval
    return mul_intervals(i1, reciprocal_i2) 