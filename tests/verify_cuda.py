try:
    from cuda.bindings import driver
    from cuda.bindings import cudart
except ImportError as e:
    print(f"ImportError: {e}")
    exit(1)

def check_cuda():
    print("Initializing CUDA using cuda.bindings.driver...")
    
    # helper to check error
    def check_err(err, msg):
        if err != 0:
            print(f"{msg} failed with error: {err}")
            return False
        return True

    # cuInit(0)
    err, = driver.cuInit(0)
    if not check_err(err, "cuInit"): return

    # cuDeviceGetCount
    err, count = driver.cuDeviceGetCount()
    if not check_err(err, "cuDeviceGetCount"): return
    
    print(f"CUDA-Python initialized successfully.")
    print(f"Number of CUDA devices found: {count}")

    for i in range(count):
        err, device = driver.cuDeviceGet(i)
        if not check_err(err, f"cuDeviceGet({i})"): continue
        
        err, name = driver.cuDeviceGetName(128, device)
        if not check_err(err, f"cuDeviceGetName({i})"): continue
        
        print(f"Device {i}: {name.decode('utf-8').strip()}")

if __name__ == "__main__":
    check_cuda()
