import sys
try:
    from cuda import bindings
    print("Successfully imported cuda.bindings")
    print("dir(bindings):", dir(bindings))
    
    # Check for submodules
    if hasattr(bindings, 'driver'):
        print("dir(bindings.driver):", dir(bindings.driver))
    
    if hasattr(bindings, 'cudart'):
        print("dir(bindings.cudart):", dir(bindings.cudart))
        
except ImportError as e:
    print(f"Failed to import bindings: {e}")

try:
    import cuda.cuda
    print("Successfully imported cuda.cuda")
except ImportError as e:
    print(f"Failed to import cuda.cuda: {e}")
