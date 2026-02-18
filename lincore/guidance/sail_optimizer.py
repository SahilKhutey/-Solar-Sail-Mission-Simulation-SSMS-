import numpy as np

def optimal_steering_law(r, v, target_element, direction='maximize'):
    """
    Computes the optimal sail pitch angle (alpha*) to maximize the rate of change
    of a specific orbital element (e.g., semi-major axis 'a' for energy gain).
    
    Based on: "Solar Sail Mission Design", McInnes.
    
    r, v: State vectors (km, km/s)
    target_element: 'energy' or 'a' (semi-major axis), 'i' (inclination)
    """
    # 2. Optimal Steering Vector Logic
    # The optimal normal n must lie in the plane spanned by Sun vector s and Velocity vector v.
    # Ref: McInnes, "Solar Sailing", Section 4.3.1 (tangential thrust)
    
    # Sun vector (assuming Sun at origin and r is Heliocentric SC pos)
    # s points from Sun to SC.
    # Wait, force formula uses s_hat from Sun to SC?
    # Usually we define cone angle alpha relative to Sun line.
    
    s = r # Sun to SC
    s_norm = np.linalg.norm(s)
    if s_norm == 0: return np.array([1, 0, 0])
    s_hat = s / s_norm
    
    # Velocity direction
    v_norm = np.linalg.norm(v)
    if v_norm == 0: return s_hat
    v_hat = v / v_norm
    
    # Plane basis
    # We want to maximize force component along v (maximize energy/power).
    # Force F ~ (n . s_hat)^2 * n  (Ideally, if n . s_hat > 0)
    # Actually F ~ (n . s_hat)^2 * n if we consider s_hat is Sun->SC.
    # Wait, if n is normal pointing away from sun side.
    # Let n . s_hat = -cos(alpha) ?
    # Let's restrict n such that n . s_hat < 0 (pointing towards sun).
    # Formula in srp.py: cos_theta = n_eci . (-s_hat).
    # So n should generally oppose s_hat.
    
    # Let u = -s_hat (Vector pointing TO Sun).
    u = -s_hat
    
    # We span plane with u and v_hat.
    # Orthogonal basis: u, w
    # w = (component of v perp to u)
    proj = np.dot(v_hat, u)
    w_vec = v_hat - proj * u
    w_norm = np.linalg.norm(w_vec)
    
    if w_norm < 1e-6:
        # v is parallel to u (radial motion).
        # Optimal alpha is 0 (normal along u)? 
        # If moving away from sun, max force is alpha=0.
        return u
        
    w = w_vec / w_norm
    
    # n = cos(alpha) * u + sin(alpha) * w
    # We invoke the standard 35.26 degree result if v is perpendicular (proj=0).
    # But generally, we optimize alpha.
    # Maximize J(alpha) = cos^2(alpha) * (n . v_hat)
    # n . v_hat = cos(alpha)*(u.v) + sin(alpha)*(w.v)
    # Let v_u = u.v, v_w = w.v
    # J(alpha) = cos^2(alpha) * (v_u cos(alpha) + v_w sin(alpha))
    
    # We can solve dJ/dalpha = 0 numerically or analytically.
    # For now, numerical golden section search is robust and fast enough (few iterations).
    
    def objective(alpha):
        # alpha in [-pi/2, pi/2]
        ca = np.cos(alpha)
        if ca < 0: return -1e9 # Invalid, backside
        sa =  np.sin(alpha)
        n_test = ca * u + sa * w
        
        # J = (n . u)^2 * (n . v)
        # Note: n . u = ca
        # So J = ca^2 * np.dot(n_test, v_hat)
        return ca**2 * np.dot(n_test, v_hat)
        
    # Search range: [-pi/3, pi/3] usually covers typical sail maneuvers
    import scipy.optimize
    res = scipy.optimize.minimize_scalar(lambda a: -objective(a), bounds=(-np.pi/2, np.pi/2), method='bounded')
    
    alpha_opt = res.x
    n_opt = np.cos(alpha_opt) * u + np.sin(alpha_opt) * w
    
    return n_opt

def get_optimal_attitude(r, v):
    """
    Returns optimal Quaternion for max energy gain.
    """
    return np.array([1, 0, 0, 0]) # Placeholder
