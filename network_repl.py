from cell import make_cell
from propagator import make_propagator
from graph_visualizer import GraphVisualizer
from tms import make_premise, supported_value
import sys

class PropNetworkREPL:
    def __init__(self):
        self.cells = {}
        self.propagators = {}
        self.premises = {}
        self.visualizer = GraphVisualizer()
        self._setup_visualizer()
        
    def _setup_visualizer(self):
        """Set up visualization for both cells and propagators to track network changes."""
        import propagator
        import cell
        propagator.set_visualizer(self.visualizer)
        cell.set_visualizer(self.visualizer)
    
    def run(self, use_visualization=True):
        """Start the propagation network REPL."""
        self.use_visualization = use_visualization
        
        print("Propagation Network Interactive Environment")
        print("\nAvailable commands:")
        
        print("\nCell operations:")
        print("  new_cell <name>           - Create a new cell")
        print("  set <cell> <value>        - Set a cell's value")
        print("  set <cell> [low,high]     - Set a cell to an interval")
        print("  get <cell>                - Get a cell's current value")
        
        print("\nPropagator operations:")
        print("  add <cell1> <cell2> <out> - Create adder: out = cell1 + cell2")
        print("  sub <cell1> <cell2> <out> - Create subtractor: out = cell1 - cell2")
        print("  mul <cell1> <cell2> <out> - Create multiplier: out = cell1 * cell2")
        print("  div <cell1> <cell2> <out> - Create divider: out = cell1 / cell2")
        
        print("\nTruth Maintenance System (TMS):")
        print("  new_premise <name>        - Create a new premise")
        print("  set_supported <cell> <value> <premise1> [premise2 ...] - Set cell with premise support")
        print("  premises                  - List all premises")
        
        print("\nVisualization:")
        print("  show                      - Visualize current network")
        print("  cells                     - List all cells and values")
        
        print("\nOther:")
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
                    self.run(use_visualization=self.use_visualization)  # Keep same visualization setting
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
            
        elif cmd == "new_premise":
            if len(args) != 1:
                print("Usage: new_premise <name>")
                return
            self._create_premise(args[0])
            
        elif cmd == "premises":
            self._list_premises()
            
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
            
        elif cmd == "show":
            if self.use_visualization:
                self.visualizer.draw()
            else:
                print("Visualization is disabled. Run with --no_vis flag to enable.")
            
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
        print(f"{cell_name}: {value}")
    
    def _list_cells(self):
        print("\nCurrent cells:")
        for name, cell in self.cells.items():
            print(f"{name}: {cell.content()}")
    
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
        
        # Check if all premises exist
        premises = []
        for p_name in premise_names:
            if p_name not in self.premises:
                print(f"Premise '{p_name}' not found. Create it with 'new_premise {p_name}'")
                return
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

    def _create_premise(self, name):
        """Create a new premise with the given name."""
        if name in self.premises:
            print(f"Premise '{name}' already exists")
            return
        
        premise = make_premise(name)
        self.premises[name] = premise
        print(f"Created premise: {name}")

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
        

if __name__ == "__main__":
    repl = PropNetworkREPL()
    repl.run()   