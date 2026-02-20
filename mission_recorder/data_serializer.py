import pandas as pd
import os
import numpy as np

class DataSerializer:
    """
    Handles the serialization of simulation data.
    Uses Parquet for efficient storage of time-series data.
    """
    def __init__(self):
        pass

    def save_timeseries(self, data: dict, filepath: str):
        """
        Saves time-series dictionary (arrays) to a Parquet file.
        
        Args:
            data: Dictionary where keys are column names and values are lists/arrays.
            filepath: Destination file path (should end in .parquet).
        """
        try:
            df = pd.DataFrame(data)
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Use 'pyarrow' engine for better compatibility and performance
            df.to_parquet(filepath, engine='pyarrow', index=False)
            return True
        except Exception as e:
            print(f"Error saving timeseries to {filepath}: {e}")
            return False

    def load_timeseries(self, filepath: str) -> pd.DataFrame:
        """
        Loads time-series data from a Parquet file.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        return pd.read_parquet(filepath, engine='pyarrow')
