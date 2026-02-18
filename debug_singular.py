import numpy as np
import sys
import os

# Add parent path
sys.path.append(os.path.abspath('.'))

from lincore.attitude.rigid_body import attitude_derivative

def test():
    print("Testing attitude_derivative...")
    q = [1.0, 0.0, 0.0, 0.0]
    w = [0.01, 0.01, 2.0]
    I = [[10.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 30.0, 0.0]]
    tau = [0.0, 0.0, 0.0]
    
    try:
        dq, dw = attitude_derivative(q, w, I, tau)
        print("Success!")
        print(f"dq: {dq}")
        print(f"dw: {dw}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
