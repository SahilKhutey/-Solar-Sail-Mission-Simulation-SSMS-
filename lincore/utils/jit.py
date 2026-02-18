try:
    from numba import jit
    HAS_NUMBA = True
    # Standard Nopython JIT
    num_jit = jit(nopython=True, cache=True)
except ImportError:
    HAS_NUMBA = False
    # Dummy decorator
    def num_jit(func):
        return func
