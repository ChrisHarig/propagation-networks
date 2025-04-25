from cell import make_cell
from propagator_constructors import adder, multiplier, constant, subtractor, divider

###----------------------------SMALL NETWORK EXAMPLES----------------------------###

def product_constraint(x, y, total):
    """
    Creates a network of propagators that maintain the relationship total = x * y.
    
    This is bidirectional - any of the three values can be computed from the other two:
    - If x and y are known, total will be set to x * y
    - If total and x are known, y will be set to total / x
    - If total and y are known, x will be set to total / y
    
    Args:
        x: Cell representing the first factor
        y: Cell representing the second factor
        total: Cell representing the product
    """
    # Forward direction: total = x * y
    multiplier()(x, y, total)
    # Backward directions:
    # x = total / y
    divider()(total, y, x)
    # y = total / x
    divider()(total, x, y)

def sum_constraint(a, b, total):
    """
    Creates a network of propagators that maintain the relationship total = a + b.
    
    This is bidirectional - any of the three values can be computed from the other two:
    - If a and b are known, total will be set to a + b
    - If total and a are known, b will be set to total - a
    - If total and b are known, a will be set to total - b
    
    Args:
        a: Cell representing the first addend
        b: Cell representing the second addend
        total: Cell representing the sum
    """
    # Forward direction: total = a + b
    adder()(a, b, total)
    # Backward directions:
    # b = total - a
    subtractor()(total, a, b)
    # a = total - b
    subtractor()(total, b, a)

def subtractor_constraint(minuend, subtrahend, difference):
    """
    Creates a network of propagators that maintain the relationship:
    minuend - subtrahend = difference
    
    This is bidirectional:
    - If minuend and subtrahend are known, difference will be computed
    - If difference and subtrahend are known, minuend will be computed
    - If minuend and difference are known, subtrahend will be computed
    
    Args:
        minuend: Cell representing the number being subtracted from
        subtrahend: Cell representing the number being subtracted
        difference: Cell representing the result of the subtraction
    """
    # Create the subtraction constraint: minuend - subtrahend = difference
    subtractor()(minuend, subtrahend, difference)
    
    # Create the inverse constraint: minuend = difference + subtrahend
    adder()(difference, subtrahend, minuend)
    
    # Create the inverse constraint: subtrahend = minuend - difference
    subtractor()(minuend, difference, subtrahend)

def divider_constraint(dividend, divisor, quotient):
    """
    Creates a network of propagators that maintain the relationship:
    dividend / divisor = quotient
    
    This is bidirectional:
    - If dividend and divisor are known, quotient will be computed
    - If quotient and divisor are known, dividend will be computed
    - If dividend and quotient are known, divisor will be computed
    
    Args:
        dividend: Cell representing the number being divided
        divisor: Cell representing the number to divide by
        quotient: Cell representing the result of the division
    """
    # Create the division constraint: dividend / divisor = quotient
    divider()(dividend, divisor, quotient)
    
    # Create the inverse constraint: dividend = quotient * divisor
    multiplier()(quotient, divisor, dividend)
    
    # Create the inverse constraint: divisor = dividend / quotient
    divider()(dividend, quotient, divisor)

###--------------------------------TEST NETWORK EXAMPLES--------------------------------###

def fahrenheit_celsius_converter(f, c):
    """
    Creates a network of propagators that maintain the relationship between
    Fahrenheit and Celsius temperatures: F = 9/5 * C + 32
    
    This is bidirectional:
    - If F is known, C will be computed as (F - 32) * 5/9
    - If C is known, F will be computed as 9/5 * C + 32
    
    Args:
        f: Cell representing temperature in Fahrenheit
        c: Cell representing temperature in Celsius
    """
    # Create intermediate cells and constants
    thirty_two = make_cell("32")
    thirty_two.add_content(32)
    
    five = make_cell("5")
    five.add_content(5)
    
    nine = make_cell("9")
    nine.add_content(9)
    
    # Create intermediate cells for the formula
    f_minus_32 = make_cell("f_minus_32")
    c_times_9 = make_cell("c*9")
    
    # Set up the bidirectional constraints based on the formula:
    # F = 9/5 * C + 32
    
    # Part 1: F = F_minus_32 + 32
    sum_constraint(f_minus_32, thirty_two, f)
    
    # Part 2: C * 9 = C_times_9
    product_constraint(c, nine, c_times_9)
    
    # Part 3: F_minus_32 * 5 = C_times_9
    product_constraint(f_minus_32, five, c_times_9) 