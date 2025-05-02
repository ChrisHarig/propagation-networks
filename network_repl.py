from cell import make_cell
from propagator import make_propagator
from tms import make_premise, supported_value, kick_out, bring_in, premise_in, _current_worldview
from layers import base_layer_value
import sys

class PropNetworkREPL:
    def __init__(self):
        self.cells = {}
        self.propagators = {}
        self.premises = {}
        
    def run(self, use_visualization=False):
        """Start the propagation network REPL."""
        print("Propagation Network Interactive Environment")
        print("\nAvailable commands:")
        
        print("\nCell operations:")
        print("  new_cell <name>           - Create a new cell")
        print("  set <cell> <value>        - Set a cell's value")
        print("  set <cell> [low,high]     - Set a cell to an interval")
        print("  set_supported <cell> <value> <premise1> [premise2 ...] - Set cell with premise support")
        print("  get <cell>                - Get a cell's current value")
        
        print("\nPropagator operations:")
        print("  add <cell1> <cell2> <out> - Create adder: out = cell1 + cell2")
        print("  sub <cell1> <cell2> <out> - Create subtractor: out = cell1 - cell2")
        print("  mul <cell1> <cell2> <out> - Create multiplier: out = cell1 * cell2")
        print("  div <cell1> <cell2> <out> - Create divider: out = cell1 / cell2")
        
        print("\nTruth Maintenance System (TMS):")
        print("  premises                  - List all premises")
        print("  worldview                 - Show current worldview (active premises)")
        print("  kick <premise_name>       - Remove a premise from worldview")
        print("  bring <premise_name>      - Add a premise to worldview")
        
        print("\nOther:")
        print("  cells                     - List all cells and values")
        print("  help                      - Show this help")
        print("  quit                      - Exit")
        
        while True:
            try:
                command = input("\nprop> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                if cmd == "quit":
                    break
                elif cmd == "help":
                    self.run()
                    continue
                
                self._handle_command(cmd, command[1:])
                
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _handle_command(self, cmd, args):
        """Handle a single REPL command."""
        if cmd == "new_cell":
            if len(args) != 1:
                print("Usage: new_cell <name>")
                return
            cell = make_cell(args[0])
            self.cells[args[0]] = cell
            print(f"Created cell: {args[0]}")
            
        elif cmd == "set":
            if len(args) != 2:
                print("Usage: set <cell> <value>")
                return
            self._set_cell_value(args[0], args[1])
            
        elif cmd == "set_supported":
            if len(args) < 3:
                print("Usage: set_supported <cell> <value> <premise1> [premise2 ...]")
                return
            self._set_supported_cell_value(args[0], args[1], args[2:])
            
        elif cmd == "premises":
            self._list_premises()
            
        elif cmd == "worldview":
            self._show_worldview()
            
        elif cmd == "kick":
            if len(args) != 1:
                print("Usage: kick <premise_name>")
                return
            self._kick_out_premise(args[0])
            
        elif cmd == "bring":
            if len(args) != 1:
                print("Usage: bring <premise_name>")
                return
            self._bring_in_premise(args[0])
            
        elif cmd == "get":
            if len(args) != 1:
                print("Usage: get <cell>")
                return
            self._get_cell_value(args[0])
            
        elif cmd in ["add", "sub", "mul", "div"]:
            if len(args) != 3:
                print(f"Usage: {cmd} <cell1> <cell2> <output>")
                return
            self._create_operation(cmd, args)
            
        elif cmd == "cells":
            self._list_cells()
            
        else:
            print(f"Unknown command: {cmd}")
    
    def _set_cell_value(self, cell_name, value):
        if cell_name not in self.cells:
            print(f"Cell '{cell_name}' not found")
            return
        try:
            # Check if the value is an interval notation [low,high]
            if value.startswith('[') and value.endswith(']'):
                # Extract the numbers from the interval notation
                interval_parts = value[1:-1].split(',')
                if len(interval_parts) != 2:
                    raise ValueError("Interval must have exactly two values [low,high]")
                
                low = float(interval_parts[0].strip())
                high = float(interval_parts[1].strip())
                
                # Import Interval class
                from interval import Interval
                interval_value = Interval(low, high)
                self.cells[cell_name].add_content(interval_value)
                print(f"Set {cell_name} = {interval_value}")
            else:
                # Handle regular numeric values 
                value = float(value)
                self.cells[cell_name].add_content(value)
                print(f"Set {cell_name} = {value}")
            
            self._show_network_effects()
        except ValueError as e:
            print(f"Error setting value: {str(e)}")
    
    def _get_cell_value(self, cell_name):
        if cell_name not in self.cells:
            print(f"Cell '{cell_name}' not found")
            return
        value = self.cells[cell_name].content()
        print(f"{cell_name}: {self._format_value(value)}")
    
    def _format_value(self, value):
        """Format a value for display, handling layered data."""
        if hasattr(value, 'get_layer_value') and hasattr(value, 'has_layer'):
            # Get the base value
            base = base_layer_value(value)
            
            # Build a string representing all the layers
            layers = []
            if value.has_layer('support'):
                support = value.get_layer_value('support')
                layers.append(f"support: {support}")
            
            if layers:
                return f"{base} with {', '.join(layers)}"
            return str(base)
        return str(value)
    
    def _list_cells(self):
        print("\nCurrent cells:")
        for name, cell in self.cells.items():
            content = cell.content()
            print(f"{name}: {self._format_value(content)}")
    
    def _show_network_effects(self):
        """Show how the network propagated values."""
        print("\nNetwork state after propagation:")
        self._list_cells()

    def _create_operation(self, op, args):
        """Create a propagator for basic operations."""
        cell1_name, cell2_name, output_name = args
        
        # Create cells if they don't exist
        if cell1_name not in self.cells:
            self.cells[cell1_name] = make_cell(cell1_name)
            print(f"Created cell: {cell1_name}")
        
        if cell2_name not in self.cells:
            self.cells[cell2_name] = make_cell(cell2_name)
            print(f"Created cell: {cell2_name}")
        
        if output_name not in self.cells:
            self.cells[output_name] = make_cell(output_name)
            print(f"Created cell: {output_name}")
        
        # Get the cells
        cell1 = self.cells[cell1_name]
        cell2 = self.cells[cell2_name]
        output = self.cells[output_name]
        
        # Import the appropriate constraint function
        from example_networks import sum_constraint, product_constraint, subtractor_constraint, divider_constraint
        
        # Create the appropriate propagator
        if op == "add":
            sum_constraint(cell1, cell2, output)
            print(f"Created adder: {cell1_name} + {cell2_name} = {output_name}")
        elif op == "sub":
            subtractor_constraint(cell1, cell2, output)
            print(f"Created subtractor: {cell1_name} - {cell2_name} = {output_name}")
        elif op == "mul":
            product_constraint(cell1, cell2, output)
            print(f"Created multiplier: {cell1_name} * {cell2_name} = {output_name}")
        elif op == "div":
            divider_constraint(cell1, cell2, output)
            print(f"Created divider: {cell1_name} / {cell2_name} = {output_name}")
        
        # Store the propagator in our list (though we don't have direct access to it)
        prop_name = f"{op}_{cell1_name}_{cell2_name}_{output_name}"
        self.propagators[prop_name] = True
        
        # Show the updated network state
        self._show_network_effects()

    def _set_supported_cell_value(self, cell_name, value, premise_names):
        """Set a cell's value with specified premise support."""
        if cell_name not in self.cells:
            print(f"Cell '{cell_name}' not found")
            return
        
        # Auto-create any premises that don't exist
        premises = []
        for p_name in premise_names:
            if p_name not in self.premises:
                # Create the premise automatically
                premise = make_premise(p_name)
                self.premises[p_name] = premise
                print(f"Created premise: {p_name}")
            premises.append(self.premises[p_name])
        
        try:
            # Handle interval notation similar to _set_cell_value
            if value.startswith('[') and value.endswith(']'):
                interval_parts = value[1:-1].split(',')
                if len(interval_parts) != 2:
                    raise ValueError("Interval must have exactly two values [low,high]")
                
                low = float(interval_parts[0].strip())
                high = float(interval_parts[1].strip())
                
                from interval import Interval
                interval_value = Interval(low, high)
                supported = supported_value(interval_value, premises)
                self.cells[cell_name].add_content(supported)
                print(f"Set {cell_name} = {interval_value} supported by {', '.join(premise_names)}")
            else:
                # Handle regular numeric values
                value = float(value)
                supported = supported_value(value, premises)
                self.cells[cell_name].add_content(supported)
                print(f"Set {cell_name} = {value} supported by {', '.join(premise_names)}")
            
            self._show_network_effects()
        except ValueError as e:
            print(f"Error setting value: {str(e)}")

    def _list_premises(self, verbose=True):
        """List all premises in the system."""
        if verbose:
            print("\nAvailable premises:")
        
        if not self.premises:
            if verbose:
                print("  No premises defined")
            return
        
        for name, premise in self.premises.items():
            if verbose:
                print(f"  {name}")

    def _show_worldview(self):
        """Show all premises in the current worldview."""
        print("\nCurrent worldview (active premises):")
        
        if not _current_worldview:
            print("  No premises are currently active")
            return
        
        for premise in _current_worldview:
            premise_name = premise.name if hasattr(premise, 'name') else str(premise)
            print(f"  {premise_name}")

    def _kick_out_premise(self, premise_name):
        """Remove a premise from the current worldview."""
        if premise_name not in self.premises:
            print(f"Premise '{premise_name}' not found")
            return
        
        # Check if the premise is in the worldview first
        if not premise_in(premise_name):
            print(f"Premise '{premise_name}' is not in the current worldview")
            return
        
        # Kick out the premise
        kick_out(premise_name)
        print(f"Kicked out premise '{premise_name}' from the worldview")
        
        # Show the updated network state
        self._show_network_effects()

    def _bring_in_premise(self, premise_name):
        """Add a premise to the current worldview."""
        if premise_name not in self.premises:
            print(f"Premise '{premise_name}' not found")
            return
        
        # Check if the premise is already in the worldview
        if premise_in(premise_name):
            print(f"Premise '{premise_name}' is already in the worldview")
            return
        
        # Bring in the premise
        bring_in(self.premises[premise_name])
        print(f"Brought in premise '{premise_name}' to the worldview")
        
        # Show the updated network state
        self._show_network_effects()

if __name__ == "__main__":
    repl = PropNetworkREPL()
    repl.run()   