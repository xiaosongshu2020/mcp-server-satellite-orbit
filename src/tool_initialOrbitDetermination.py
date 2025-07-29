import subprocess
import os
from typing import Union


def initial_orbit_determination(
    longitude: float,
    latitude: float,
    altitude: float,
    obs_type: int,
    data_file: str
) -> str:
    """
    Call the initial orbit determination program to calculate satellite orbit parameters
    
    Observation Types:
        1 - AH: Azimuth/Elevation (Horizontal angle measurements)
        2 - AD: Right Ascension/Declination (Celestial coordinate measurements)
        3 - RRD: Range/Range Rate (Radar distance and velocity measurements)
    
    Parameters:
        longitude (float): Station longitude in degrees (-180 to 180)
        latitude (float): Station latitude in degrees (-90 to 90)
        altitude (float): Station altitude in meters
        obs_type (int): Observation type (1 for AH, 2 for AD, 3 for RRD)
        data_file (str): Path to observation data file
    
    Returns:
        str: Program execution output
        
    Exceptions:
        subprocess.CalledProcessError: Raised when program execution fails
        FileNotFoundError: Raised when executable file is not found
    """
    # Fixed executable path
    executable_path = "bin/initialOrbitDetermination.exe"
    
    # Validate observation type and convert to string
    obs_type_map = {1: "AH", 2: "AD", 3: "RRD"}
    if obs_type not in obs_type_map:
        raise ValueError(f"Observation type must be 1, 2, or 3. Got: {obs_type}")
    
    obs_type_str = obs_type_map[obs_type]
    
    # Check if executable file exists
    if not os.path.exists(executable_path):
        raise FileNotFoundError(f"Executable file not found: {executable_path}")
    
    # Check if data file exists
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    # Build command line arguments
    cmd = [
        executable_path,
        str(longitude),
        str(latitude),
        str(altitude),
        obs_type_str,
        data_file
    ]
    
    try:
        # Execute command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Initial orbit determination program execution failed:\nReturn code: {e.returncode}\nError output: {e.stderr}"
        raise subprocess.CalledProcessError(e.returncode, cmd, error_msg) from e
    except Exception as e:
        raise RuntimeError(f"Error executing initial orbit determination program: {str(e)}") from e


# Example usage
if __name__ == "__main__":
    # Example call (requires an actual observation data file)
    try:
        # Note: This requires an actual observation data file to run
        # result = initial_orbit_determination(
        #     longitude=116.385,
        #     latitude=39.905,
        #     altitude=50.0,
        #     obs_type=1,
        #     data_file="observations.txt"
        # )
        # print(result)
        print("Tool loaded, ready to perform initial orbit determination calculation")
    except Exception as e:
        print(f"Error: {e}")
