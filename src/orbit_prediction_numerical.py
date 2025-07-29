# 定义llm可以调用的数值轨道预报工具
import subprocess
import os


def run_orbitPrediction_numerical(
    start_time: str,
    kepler0: str,
    end_time: str,
    step: float,
    filename: str,
    ephType: int = 2,
    Cd: float = 2.2,
    amrDrag: float = 0.02,
    F107: float = 130.0,
    Ap: float = 15.0,
    reflectivity: float = 0.0,
    amrSRP: float = 0.02,
    order: int = 2,
    K_tesseral: int = 1,
    K_lunar: int = 0,
    K_lunarTide: int = 0,
    K_solor: int = 0,
    K_solarTide: int = 0,
    K_SRP: int = 0,
    K_drag: int = 0,
    K_PN: int = 0,
) -> str:
    """
    Run orbit prediction using the .exe executable.
    
    Parameters:
    -----------
    start_time : str
        Start time in format 'YYYY MM DD HH MM SS.SSS'
        Example: "2023 01 01 12 00 00.000"
    
    kepler0 : str
        Six Keplerian elements (a(km), e, i(deg), Omega(deg), omega(deg), M(deg)) as space-separated string
        Example:  "7000 0.01 45 30 60 90"
    
    end_time : str
        End time in format 'YYYY MM DD HH MM SS.SSS'
        Example: "2023 01 02 12 00 00.000"
    
    step : float
        Time step in seconds
    
    filename : str
        Output ephemeris filename
    
    ephType : int, optional (default=2)
        Ephemeris type (1: Keplerian elements, 2: position/velocity)
    
    Cd : float, optional (default=2.2)
        Drag coefficient
    
    amrDrag : float, optional (default=0.02)
        Area-to-mass ratio for drag
    
    F107 : float, optional (default=130.0)
        Solar flux index
    
    Ap : float, optional (default=15.0)
        Geomagnetic index
    
    reflectivity : float, optional (default=0.0)
        Surface reflectivity
    
    amrSRP : float, optional (default=0.02)
        Area-to-mass ratio for solar radiation pressure
    
    order : int, optional (default=2)
        Gravity model order
    
    K_tesseral : int, optional (default=1)
        Tesseral harmonics flag
    
    K_lunar : int, optional (default=0)
        Lunar perturbation flag
    
    K_lunarTide : int, optional (default=0)
        Lunar tide flag
    
    K_solor : int, optional (default=0)
        Solar perturbation flag
    
    K_solarTide : int, optional (default=0)
        Solar tide flag
    
    K_SRP : int, optional (default=0)
        Solar radiation pressure flag
    
    K_drag : int, optional (default=0)
        Atmospheric drag flag
    
    K_PN : int, optional (default=0)
        Post-Newtonian flag

    Returns:
    --------
    str: Result message indicating success or failure

    Examples:
    ---------
    # Basic usage with required parameters only
    result = run_orbitPrediction_numerical(
        start_time="2023 01 01 12 00 00.000",
        kepler_elements=[7000, 0.01, 45, 30, 60, 90],
        end_time="2023 01 02 12 00 00.000",
        step=60,
        filename="output.txt"
    )
    
    # Advanced usage with custom parameters
    result = run_orbitPrediction_numerical(
        start_time="2023 01 01 12 00 00.000",
        kepler_elements="7000 0.01 45 30 60 90",
        end_time="2023 01 02 12 00 00.000",
        step=60,
        filename="output.txt",
        ephType=1,
        Cd=2.3,
        F107=150.0,
        K_drag=1,
        K_SRP=1
    )
    """

    # Set executable path
    executable_path = "./bin/orbitPrediction_numerical.exe"

    # Check if executable exists
    if not os.path.exists(executable_path):
        return f"Error: Executable not found at {executable_path}"

    # Process kepler0 parameters - protect against i=0
    kepler_list = kepler0.split()
    if len(kepler_list) >= 3:  # Ensure we have at least 3 elements
        i = float(kepler_list[2])
        if abs(i) < 1e-7:  # If inclination is close to 0
            kepler_list[2] = "1e-7"  # Set to small non-zero value
            kepler0 = " ".join(kepler_list)

    # Build command arguments list
    cmd_args = [
        executable_path,
        str(start_time),
        str(kepler0),
        str(end_time),
        str(step),
        str(filename),
        str(ephType),
        str(Cd),
        str(amrDrag),
        str(F107),
        str(Ap),
        str(reflectivity),
        str(amrSRP),
        str(order),
        str(K_tesseral),
        str(K_lunar),
        str(K_lunarTide),
        str(K_solor),
        str(K_solarTide),
        str(K_SRP),
        str(K_drag),
        str(K_PN)
    ]
    
    try:
        # Run the executable
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Check if output file was created
        if os.path.exists(filename):
            return f"Orbit prediction completed successfully. Ephemeris saved to {filename}"
        else:
            return f"Warning: Orbit prediction completed but output file {filename} was not found"
            
    except subprocess.TimeoutExpired:
        return f"Error: Orbit prediction timed out after 300 seconds"
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Error: Orbit prediction failed with return code {e.returncode}"
        if e.stderr:
            error_msg += f"\nError output: {e.stderr}"
        return error_msg
    
    except FileNotFoundError:
        return f"Error: Executable not found at {executable_path}"
    
    except Exception as e:
        return f"Error: Unexpected error occurred: {str(e)}"


if __name__ == "__main__":
    # Example usage
    result = run_orbitPrediction_numerical(
        start_time="2023 01 01 12 00 00.000",
        kepler0="7000 0 0 0 0 0",
        end_time="2023 01 02 12 00 00.000",
        step=60,
        filename="test_output.txt"
    )
    print(result)
