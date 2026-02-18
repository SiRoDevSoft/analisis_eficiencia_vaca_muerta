 # sanitizer.py
import numpy as np

def filter_by_integrity(current_data, data_window):
    """
    Detects sensor errors based on recent historical data using Z-score.
    """
    if len(data_window) < 2:
        # Insufficient historical data
        return current_data 

    mean = np.mean(data_window)
    std_dev = np.std(data_window)

    # Handle division by zero: result is undefined
    if std_dev == 0:
        return current_data

    # Calculate the Z-score
    z_score = (current_data - mean) / std_dev

    # Outlier detection: if data is more than 3 standard deviations away, it's suspicious.
    # We return the mean to maintain signal stability for the SCADA.
    if abs(z_score) > 3:
        return mean 
    
    return current_data
