"""
Layered data system for the propagator network.

This module provides infrastructure for layering different types of information
on data, allowing separation of concerns without cluttering the code.
"""

###----------------------------LAYERS SYSTEM----------------------------###

# Dictionary of layer definitions - these are fixed at design time - assigned below
LAYERS = {}

# Base layer is the primary/essential data
class BaseLayer:
    """The fundamental layer containing the primary value."""
    
    @staticmethod
    def get_name():
        """Get the name of this layer."""
        return 'base'
    
    @staticmethod
    def has_value(obj):
        """Every object has a base value."""
        return True
    
    @staticmethod
    def get_value(obj):
        """
        Get the base value of an object.
        
        If obj is a layered datum, retrieves its base value.
        Otherwise, returns the object itself.
        """
        if hasattr(obj, 'get_layer_value'):
            return obj.get_layer_value('base')
        return obj
    
    @staticmethod
    def get_default_value():
        """Default value for the base layer."""
        from nothing import NOTHING
        return NOTHING

# SupportLayer provides infrastructure for tracking premises that justify values
class SupportLayer:
    """Layer for tracking the justification of values through premises."""
    
    @staticmethod
    def get_name():
        """Get the name of this layer."""
        return 'support'
    
    @staticmethod
    def has_value(obj):
        """Check if an object has support information."""
        if hasattr(obj, 'has_layer') and callable(obj.has_layer):
            return obj.has_layer('support')
        return False
    
    @staticmethod
    def get_value(obj):
        """
        Get the support value of an object.
        
        If obj has support information, retrieves it.
        Otherwise, returns an empty support.
        """
        if SupportLayer.has_value(obj):
            return obj.get_layer_value('support')
        return SupportLayer.get_default_value()
    
    @staticmethod
    def get_default_value():
        """Default value for the support layer (empty support)."""
        from tms import Support
        return Support()
    
    @staticmethod
    def get_procedure(name, arity):
        """
        Get the procedure for handling support in a named operation.
        
        Args:
            name: The name of the operation (e.g., 'add', 'multiply')
            arity: The number of arguments the operation takes
            
        Returns:
            A procedure that implements support handling for the operation
        """
        # Get all support handlers from the dedicated module
        from support_handlers import get_support_handlers
        handlers = get_support_handlers()
        
        # Return the handler for this operation if it exists
        return handlers.get(name)

# Register our layers
LAYERS['base'] = BaseLayer
LAYERS['support'] = SupportLayer

# Accessor functions
def get_layer(layer_name):
    """Get a layer by name."""
    return LAYERS.get(layer_name)

def layer_value(layer_name, obj): #do we want to return none if the layer is not present?
    """Get the value of a specific layer for an object."""
    layer = get_layer(layer_name)
    if layer:
        return layer.get_value(obj)
    return None

# Convenience functions
base_layer_value = lambda obj: layer_value('base', obj)
support_layer_value = lambda obj: layer_value('support', obj)

###----------------------------LAYERED DATUM----------------------------###

class LayeredDatum:
    """
    A layered datum contains a base value with additional layer information.
    """
    
    def __init__(self, base_value, **layer_values):
        """
        Create a layered datum with a base value and layer values.
        
        Args:
            base_value: The primary value for this datum
            **layer_values: Additional layers as keyword arguments
        """
        self.layers = {'base': base_value}
        for layer_name, value in layer_values.items():
            self.layers[layer_name] = value
    
    def has_layer(self, layer_name):
        """Check if this datum has the specified layer."""
        return layer_name in self.layers
    
    def get_layer_value(self, layer_name):
        """Get the value for the specified layer."""
        return self.layers.get(layer_name)
    
    def get_annotation_layers(self):
        """Get the names of all annotation layers (non-base layers)."""
        return [name for name in self.layers.keys() if name != 'base']
    
    def __str__(self):
        base = self.layers['base']
        annotations = [f"{name}: {value}" for name, value in self.layers.items() 
                      if name != 'base']
        return f"{base} with {', '.join(annotations)}"
    
    def __repr__(self):
        return f"LayeredDatum({repr(self.layers['base'])}, {', '.join(f'{k}={repr(v)}' for k, v in self.layers.items() if k != 'base')})"

def make_layered_datum(base_value, layer_dict=None):
    """
    Create a layered datum with the given base value and layer values.
    
    Args:
        base_value: The primary value
        layer_dict: Dictionary of layer names to layer values
        
    Returns:
        A LayeredDatum if there are annotation layers, otherwise just the base_value
    """
    if not layer_dict:
        return base_value
        
    # Create a layered datum with the base value and layer values
    kwargs = {k: v for k, v in layer_dict.items() if k != 'base'}
    return LayeredDatum(base_value, **kwargs)

###----------------------------LAYERED PROCEDURES----------------------------###

class LayeredMetadata:
    """
    Metadata for a layered procedure, including its name, arity, and handlers.
    """
    
    def __init__(self, name, arity, base_procedure):
        """
        Initialize layered procedure metadata.
        
        Args:
            name: Name of the procedure (e.g., 'add', 'multiply')
            arity: Number of arguments the procedure takes
            base_procedure: The function that handles the base layer
        """
        self.name = name
        self.arity = arity
        self.base_procedure = base_procedure
        self.handlers = {}  # Layer name -> handler function
    
    def get_name(self):
        """Get the name of the procedure."""
        return self.name
    
    def get_arity(self):
        """Get the arity of the procedure."""
        return self.arity
    
    def get_base_procedure(self):
        """Get the base procedure."""
        return self.base_procedure
    
    def set_handler(self, layer, handler):
        """Set a handler for a specific layer."""
        self.handlers[layer] = handler
    
    def get_handler(self, layer):
        """
        Get the handler for a specific layer.
        
        If a custom handler has been set, returns that.
        Otherwise, asks the layer for its procedure.
        """
        if layer in self.handlers:
            return self.handlers[layer]
            
        layer_obj = get_layer(layer)
        if layer_obj:
            return layer_obj.get_procedure(self.name, self.arity)    
        return None

def layered_procedure_dispatcher(metadata):
    """
    Create a function that dispatches to layer handlers appropriately.
    
    Args:
        metadata: The LayeredMetadata for this procedure
        
    Returns:
        A function that handles layered data correctly
    """
    base_procedure = metadata.get_base_procedure()
    
    def dispatcher(*args):
        # Extract base values from all arguments
        base_values = [base_layer_value(arg) for arg in args]
        
        # Apply the base procedure to get the base result
        base_result = base_procedure(*base_values)
        
        # Find annotation layers present in any arguments
        annotation_layers = set()
        for arg in args:
            if hasattr(arg, 'get_annotation_layers'):
                annotation_layers.update(arg.get_annotation_layers())
        
        # If no annotation layers, just return the base result
        if not annotation_layers:
            return base_result
            
        # Otherwise, process each applicable layer
        layer_results = {}
        for layer in annotation_layers:
            handler = metadata.get_handler(layer)
            if handler:
                layer_result = handler(base_result, *args)
                if layer_result is not None:  # Only include if handler returned something
                    layer_results[layer] = layer_result
        
        # Return a layered datum with the base result and layer results
        return make_layered_datum(base_result, layer_results)
    
    return dispatcher

def make_layered_procedure(name, arity, base_procedure):
    """
    Create a layered procedure that handles different layers independently.
    
    Args:
        name: Name of the procedure (e.g., 'add', 'multiply')
        arity: Number of arguments the procedure takes
        base_procedure: The function that handles the base layer
        
    Returns:
        A function that dispatches to appropriate layer handlers
    """
    # Create metadata about the procedure
    metadata = LayeredMetadata(name, arity, base_procedure)
    
    # Create the dispatcher function
    dispatcher = layered_procedure_dispatcher(metadata)
    
    # Attach metadata to the dispatcher (for introspection)
    dispatcher.metadata = metadata
    
    return dispatcher
