"""
Two-body problem orbit prediction module

This module provides functions for predicting satellite orbits using
classical two-body problem dynamics and Keplerian motion.
"""

import numpy as np
import math


def orbit_prediction_two_body(t0, elements0, step, duration, fnEph="eph.txt"):
    """
    Predict satellite orbit using two-body problem dynamics

    Parameters:
    t0: Initial time as [year, month, day, hour, minute, second]
    elements0: Initial Keplerian elements [a, e, i, Omega, omega, M]
    step: Time step for prediction (minutes)
    duration: Total prediction time duration (minutes)
    fnEph: Output ephemeris filename (absolute path)

    Returns:
    Final Keplerian elements at time t0 + duration
    """
    
    # Import required functions
    from dateMJD import date2mjd, mjd2date
    from orbitTools import kpl2cts, cts2kpl
    
    # Convert initial time to MJD
    time_str = f"{int(t0[0]):04d}-{int(t0[1]):02d}-{int(t0[2]):02d} {int(t0[3]):02d}:{int(t0[4]):02d}:{int(t0[5]):02d}"
    mjd0 = date2mjd(time_str)
    
    # Extract orbital elements
    a, e, i, Omega, omega, M0 = elements0
    
    # Earth's gravitational parameter (km³/s²)
    mu = 398600.4418  # GM_Earth
    
    # Calculate mean motion (rad/s)
    n = math.sqrt(mu / (a**3))
    
    # Convert step and duration from minutes to seconds
    step_sec = step * 60.0
    duration_sec = duration * 60.0
    
    # Calculate number of steps
    num_steps = int(duration_sec / step_sec) + 1
    
    # Open ephemeris file for writing
    with open(fnEph, 'w') as f:
        # Write header comment
        f.write("# Ephemeris file: MJD_day MJD_sec x(km) y(km) z(km) vx(km/s) vy(km/s) vz(km/s)\n")
        
        # Initialize current elements
        current_elements = elements0.copy()
        
        # Propagate orbit
        for i in range(num_steps):
            # Current time
            current_time_sec = i * step_sec
            current_mjd = mjd0 + current_time_sec / 86400.0
            
            # Calculate current mean anomaly
            M_current = M0 + math.degrees(n * current_time_sec)
            M_current = M_current % 360.0  # Keep in [0, 360) range
            
            # Update current elements with new mean anomaly
            current_elements[5] = M_current
            
            # Convert to Cartesian coordinates
            cartesian = kpl2cts(np.array(current_elements))
            
            # Split MJD into day and second components
            mjd_day = int(current_mjd)
            mjd_sec = (current_mjd - mjd_day) * 86400.0
            
            # Write to ephemeris file
            f.write(f"{mjd_day} {mjd_sec:.6f} {cartesian[0]:.6f} {cartesian[1]:.6f} {cartesian[2]:.6f} "
                   f"{cartesian[3]:.9f} {cartesian[4]:.9f} {cartesian[5]:.9f}\n")
    
    # Return final orbital elements
    return current_elements

if __name__ == "__main__":
    # Test the orbit prediction function
    t0 = [2000, 1, 1, 0, 0, 0]
    elements0 = [7000.0, 0, 0, 0, 0.0, 0.0]
    step = 10.0
    duration = 1440.0
    fnEph = "satellite_eph.txt"
    result = orbit_prediction_two_body(t0, elements0, step, duration, fnEph)
    print(result)