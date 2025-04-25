# Propagation Networks Implementation

This project is an implementation of the propagation networks computation model described in the MIT thesis ["Propagation Networks: A Flexible and Expressive Substrate for Computation"](https://dspace.mit.edu/bitstream/handle/1721.1/54635/603543210-MIT.pdf) by Alexey Radul.

This is a work in progress.

## Overview

Propagation networks implemented in python. 

## Usage

There are two ways to use this implementation:

1. **Interactive REPL Mode**
   ```bash
   python main.py repl
   ```
   This starts an interactive environment where you can create and experiment with propagation networks using simple commands. Perfect for learning and exploring how propagation networks work.

2. **Developer Mode**
   Modify the source code directly to create more complex networks and add new functionality. See the example networks in `example_networks.py` for reference.
   ```bash
   python main.py
   ```
   This runs the predefined tests and examples.

## Open Questions 
-How do we handle contradictions in the long term? 
-How should we handle constants in cells that should not change? Should we at all? (Sparked by div by 0 error) 
-How do we graph these networks in a live view? 
-What issues arise with chaining propagator commands? 
-How and to which generics should we extend our system to support? 
-How do we implement TMS and worldviews? 
-How do we visualize TMS and what details do we want available to user? 

## References

- Radul, A. (2009). "Propagation Networks: A Flexible and Expressive Substrate for Computation." MIT. 