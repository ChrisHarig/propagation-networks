from typing import Dict, Tuple, Callable, Any
import inspect

### DEAD CODE - for goosey woosey 

class MultiMethod:
    def __init__(self, name):
        self.name = name
        self.typemap = {}
    
    def __call__(self, *args):
        types = tuple(type(arg) for arg in args)
        
        # Try to find an exact match
        func = self.typemap.get(types)
        if func is not None:
            return func(*args)
        
        # Find the best match based on the method resolution order
        applicable = []
        for signature, func in self.typemap.items():
            if len(signature) == len(types):
                if all(issubclass(actual, formal) for actual, formal in zip(types, signature)):
                    applicable.append((signature, func))
        
        if not applicable:
            raise TypeError(f"No matching method for {self.name}{types}")
        
        # Sort by the distance in the inheritance hierarchy - GPT wrote this part, look at inspet if issues
        def type_distance(types_pair):
            return sum(len(inspect.getmro(actual)) - len(inspect.getmro(formal))
                      for actual, formal in zip(types_pair[0], types))
        
        applicable.sort(key=lambda x: type_distance(x))
        
        # Check for ambiguity
        if len(applicable) >= 2 and type_distance(applicable[0]) == type_distance(applicable[1]):
            raise TypeError(f"Ambiguous dispatch for {self.name}{types}")
        
        return applicable[0][1](*args)
    
    def register(self, *types):
        def decorator(func):
            self.typemap[types] = func
            return self
        return decorator





