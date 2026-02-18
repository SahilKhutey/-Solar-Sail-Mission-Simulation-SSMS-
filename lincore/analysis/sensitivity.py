import numpy as np

def sobol_sensitivity(model_func, problem, n_samples=1000):
    """
    Perform Sobol Sensitivity Analysis (First-Order Indices).
    
    model_func: Function that takes (N_samples, D_dims) input matrix.
        Returns output vector (N_samples,).
        
    problem: Dict with 'num_vars', 'names', 'bounds'.
    """
    D = problem['num_vars']
    N = n_samples
    
    # Generate Saltelli sampling matrices
    # A, B are matrices of size (N, D)
    # Using simple uniform random for demo (should be QMC ideally)
    bounds = np.array(problem['bounds'])
    low = bounds[:,0]
    high = bounds[:,1]
    
    A = np.random.uniform(size=(N, D)) * (high - low) + low
    B = np.random.uniform(size=(N, D)) * (high - low) + low
    
    # Construct C_i matrices
    # For each dimension i, C_i consists of B where col i is from A
    
    # Evaluate model
    y_A = model_func(A)
    y_B = model_func(B)
    
    f0_sq = np.mean(y_A)**2
    total_var = np.var(y_A)
    
    indices = {}
    
    for i in range(D):
        AB_i = B.copy()
        AB_i[:, i] = A[:, i]
        
        y_AB_i = model_func(AB_i)
        
        # Sobol First Order Estimator
        # V_i = Var(E(Y|X_i)) ~ (1/N) sum(y_B * (y_AB_i - y_A)) + ...
        # Standard: (1/N) * sum(y_A * y_AB_i) - f0^2
        
        # Saltelli 2002/2010 estimator for S1
        # S1 = (1/N sum(y_B * (y_AB_i - y_A))) / Var(Y) ?
        # Or simpler:
        
        term = np.mean(y_A * y_AB_i)
        V_i = term - f0_sq
        S1 = V_i / total_var
        
        indices[problem['names'][i]] = S1
        
    return indices
