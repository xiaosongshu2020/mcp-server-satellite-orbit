import os
import subprocess

def run_satellite_observation(
    ts: float,
    step: float,
    te: float,
    longitude: float,
    latitude: float,
    altitude: float,
    obs_type: int,
    min_ele: float,
    solar_distance: float,
    lunar_distance: float,
    fn_eph: str,
    fn_data: str = None
) -> str:
    """
    Run the satellite observation program to calculate satellite observation data.
    
    Parameters:
    -----------
    ts : float
        Start time in Modified Julian Date (MJD)
    step : float
        Time step in seconds
    te : float
        End time in Modified Julian Date (MJD)
    longitude : float
        Observer longitude in degrees
    latitude : float
        Observer latitude in degrees
    altitude : float
        Observer altitude in meters
    obs_type : int
        Observation type (11-19, see documentation)
    min_ele : float
        Minimum elevation angle in degrees
    solar_distance : float
        Minimum angular distance from Sun in degrees
    lunar_distance : float
        Minimum angular distance from Moon in degrees
    fn_eph : str
        Satellite ephemeris filename
    fn_data : str, optional
        Observation data output filename
    
    Returns:
    --------
    str: Result message indicating success or failure
    """
    
    # Set executable path
    executable_path = "./bin/observation.exe"
    
    # Check if executable exists
    if not os.path.exists(executable_path):
        return f"Error: Observation executable not found at {executable_path}"
    
    # Check if ephemeris file exists
    if not os.path.exists(fn_eph):
        return f"Error: Ephemeris file not found: {fn_eph}"
    
    # Build command arguments list
    cmd_args = [
        executable_path,
        str(ts),
        str(step),
        str(te),
        str(longitude),
        str(latitude),
        str(altitude),
        str(obs_type),
        str(min_ele),
        str(solar_distance),
        str(lunar_distance),
        fn_eph
    ]
    
    # Add optional data output filename if provided
    if fn_data:
        cmd_args.append(fn_data)
    
    try:
        # Run the executable
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Check if output file was created (if specified)
        success_msg = "Satellite observation calculation completed successfully."
        if fn_data and os.path.exists(fn_data):
            success_msg += f" Observation data saved to {fn_data}"
        elif fn_data:
            success_msg += f" Warning: Output file {fn_data} was not created"
        
        return success_msg
            
    except subprocess.TimeoutExpired:
        return f"Error: Satellite observation calculation timed out after 300 seconds"
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Error: Satellite observation failed with return code {e.returncode}"
        if e.stderr:
            error_msg += f"\nError output: {e.stderr}"
        return error_msg
    
    except FileNotFoundError:
        return f"Error: Observation executable not found at {executable_path}"
    
    except Exception as e:
        return f"Error: Unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    # Example usage
    result = run_satellite_observation(
        ts=51544.0,
        step=60.0,
        te=51545.0,
        longitude=-75.0,
        latitude=40.0,
        altitude=100.0,
        obs_type=11,
        min_ele=10.0,
        solar_distance=5.0,
        lunar_distance=5.0,
        fn_eph="satellite_ephemeris.txt",
        fn_data="observation_data.txt"
    )
    print(result)