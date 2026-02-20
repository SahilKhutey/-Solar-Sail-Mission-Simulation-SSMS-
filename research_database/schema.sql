-- Research Database Schema

-- Table to track physics model versions and code versions
CREATE TABLE IF NOT EXISTS physics_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    srp_model TEXT NOT NULL,
    integrator TEXT NOT NULL,
    structural_model TEXT NOT NULL,
    environment_model TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store high-level run metadata and parameters
CREATE TABLE IF NOT EXISTS campaign_runs (
    run_id TEXT PRIMARY KEY,
    campaign_id TEXT,
    
    -- Parameters
    sail_area REAL,
    mass REAL,
    reflectivity REAL,
    thickness REAL,
    launch_altitude REAL,
    steering_law TEXT,
    
    -- Metrics (Outcomes)
    time_of_flight REAL,
    final_energy REAL,
    escape_velocity REAL,
    max_stress REAL,
    max_temp REAL,
    min_distance_sun REAL,
    
    -- Flags
    escape_flag BOOLEAN,
    structural_failure BOOLEAN,
    thermal_failure BOOLEAN,
    stability_score REAL,
    convergence_flag BOOLEAN,
    
    -- System
    duration_seconds REAL,
    start_time TIMESTAMP,
    git_hash TEXT,
    
    FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id)
);

-- Table for campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    description TEXT,
    start_date TIMESTAMP,
    status TEXT
);
