# server.py
from mcp.server.fastmcp import FastMCP
import numpy as np

# Create an MCP server
mcp = FastMCP("mcp-server-satOrbit")

# 1 tools about orbital basics

# 1.1 Convert Keplerian elements to Cartesian coordinates
@mcp.tool()
def kpl2cts(elements: list[float]) -> list[float]:
    """
    Convert Keplerian elements to Cartesian coordinates
    
    Parameters:
    elements: List of 6 Keplerian elements:
        elements[0]: a - semi-major axis (unit: km)
        elements[1]: e - eccentricity (dimensionless, 0 ≤ e < 1)
        elements[2]: i - inclination (unit: degrees, 0° to 180°)
        elements[3]: C_omega - longitude of ascending node/RAAN (unit: degrees, 0° to 360°)
        elements[4]: omega - argument of periapsis (unit: degrees, 0° to 360°)
        elements[5]: M - mean anomaly (unit: degrees, 0° to 360°)
    
    Returns:
    list: List of 6 Cartesian elements [x, y, z, vx, vy, vz]
        Position: x, y, z in km (Earth-centered inertial frame)
        Velocity: vx, vy, vz in km/s
    
    Example:
    kpl2cts([7000.0, 0.001, 45.0, 90.0, 0.0, 0.0])
    """
    import src.orbitTools as orbitTools
    
    # Convert input list to numpy array to avoid modifying the original list
    elements_array = np.array(elements, dtype=float)
    
    # Call the orbital tools function
    result = orbitTools.kpl2cts(elements_array)
    
    # Convert numpy array back to Python list
    return result.tolist()

# 1.2 Convert Cartesian coordinates to Keplerian elements
@mcp.tool()
def cts2kpl(cartesian: list[float]) -> list[float]:
    """
    Convert Cartesian coordinates to Keplerian elements
    
    Parameters:
    cartesian: List of 6 Cartesian elements:
        cartesian[0-2]: x, y, z - position components (unit: km)
        cartesian[3-5]: vx, vy, vz - velocity components (unit: km/s)
        (All in Earth-centered inertial coordinate frame)
    
    Returns:
    list: List of 6 Keplerian elements:
        [0]: a - semi-major axis (unit: km)
        [1]: e - eccentricity (dimensionless)
        [2]: i - inclination (unit: degrees)
        [3]: C_omega - longitude of ascending node/RAAN (unit: degrees)
        [4]: omega - argument of periapsis (unit: degrees)
        [5]: M - mean anomaly (unit: degrees)
    
    Example:
    cts2kpl([7000.0, 0.0, 0.0, 0.0, 7.5, 0.0])
    """
    import src.orbitTools as orbitTools
    
    # Convert input list to numpy array
    cartesian_array = np.array(cartesian, dtype=float)
    
    # Call the orbital tools function
    result = orbitTools.cts2kpl(cartesian_array)
    
    # Convert numpy array back to Python list
    return result.tolist()

# 1.3 convert date to Modified Julian date
@mcp.tool()
def date2mjd(date: str) -> float:
    """
    Convert date to Modified Julian Date
    
    Parameters:
    date: Date string in format "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD"
    
    Returns:
    float: Modified Julian Date
    
    Example:
    date2mjd("2000-01-01 00:00:00") returns 51544.0
    date2mjd("2000-01-01") returns 51544.0
    """
    from src.dateMJD import date2mjd
    mjd = date2mjd(date)
    return mjd

# 1.4 convert Modified Julian date to date
@mcp.tool()
def mjd2date(mjd: float) -> str:
    """
    Convert Modified Julian Date to date
    
    Parameters:
    mjd: Modified Julian Date
    
    Returns:
    str: Date string in format "YYYY-MM-DD HH:MM:SS"
    
    Example:
    mjd2date(51544.0) returns "2000-01-01 00:00:00"
    mjd2date(51544.5) returns "2000-01-01 12:00:00"
    """
    # Convert MJD to Julian Date
    from src.dateMJD import mjd2date
    date_str = mjd2date(mjd)
    return date_str

# 2 orbit prediction

# 2.1 orbit prediction in two-body problem
@mcp.tool()
def orbit_prediction_two_body(
    t0: list[float],
    elements0: list[float],
    step: float,
    duration: float,
    fnEph: str = "eph.txt"
) -> str:
    """
    Predict satellite orbit using two-body problem dynamics
    
    Parameters:
    t0: Initial time as [year, month, day, hour, minute, second]
    elements0: Initial Keplerian elements [a, e, i, Omega, omega, M] 
        a - semi-major axis (km)
        e - eccentricity (dimensionless)
        i - inclination (degrees)
        Omega - longitude of ascending node/RAAN (degrees)
        omega - argument of periapsis (degrees)
        M - mean anomaly (degrees)
    step: Time step for prediction (minutes)
    duration: Total prediction time duration (minutes)
    fnEph: Output ephemeris filename (absolute path)
        Format: MJD_day, MJD_sec, x, y, z, vx, vy, vz
    
    Returns:
    str: Result message indicating success and final Keplerian elements

    Example:
    orbit_prediction_two_body(
        [2000, 1, 1, 0, 0, 0],     # Year 2000, Jan 1, 00:00:00
        [7000.0, 0.001, 45.0, 90.0, 0.0, 0.0],  # Initial orbital elements
        10.0,                       # 10-minute steps
        1440.0,                     # Predict for 1 day (1440 minutes)
        "c:/satellite_eph.txt"         # Output file
    )
    """
    from src.orbit_prediction_two_body import orbit_prediction_two_body
    elements1 = orbit_prediction_two_body(t0, elements0, step, duration, fnEph)
    result = f"orbit prediction successful, ephemeris saved to {fnEph}.\n"
    result = result + f"Final Keplerian elements: {elements1}"
    # Return the final Keplerian elements
    return result

# 2.2 numerical high-precision orbit prediction
@mcp.tool()
def orbit_prediction_numerical(
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
        Example: "7000 0.01 45 30 60 90"
    
    end_time : str
        End time in format 'YYYY MM DD HH MM SS.SSS'
        Example: "2023 01 02 12 00 00.000"
    
    step : float
        Time step in seconds
    
    filename : str
        Output ephemeris filename (absolute path)
    
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
    str: Result message indicating success
    
    Examples:
    ---------
    # Basic usage with required parameters only
    result = orbit_prediction_numerical(
        start_time="2023 01 01 12 00 00.000",
        kepler_elements=[7000, 0.01, 45, 30, 60, 90],
        end_time="2023 01 02 12 00 00.000",
        step=60,
        filename="output.txt"
    )
    
    # Advanced usage with custom parameters
    result = orbit_prediction_numerical(
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
    from src.orbit_prediction_numerical import run_orbitPrediction_numerical
    
    # Call the orbit prediction function
    result = run_orbitPrediction_numerical(
        start_time=start_time,
        kepler0=kepler0,
        end_time=end_time,
        step=step,
        filename=filename,
        ephType=ephType,
        Cd=Cd,
        amrDrag=amrDrag,
        F107=F107,
        Ap=Ap,
        reflectivity=reflectivity,
        amrSRP=amrSRP,
        order=order,
        K_tesseral=K_tesseral,
        K_lunar=K_lunar,
        K_lunarTide=K_lunarTide,
        K_solor=K_solor,
        K_solarTide=K_solarTide,
        K_SRP=K_SRP,
        K_drag=K_drag,
        K_PN=K_PN,
    )

    return result

# 3 satellite observation
@mcp.tool()
def observation_station_satellite(
    ts: str,
    step: float,
    te: str,
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
    Calculate satellite observation data from a ground-based observer.
    
    This tool computes satellite visibility, elevation, azimuth, and other observation
    parameters for a satellite given its ephemeris data and observer location.
    
    Observation Types:
    ------------------
    11 - isAlphaDelta: Angular measurements (right ascension, declination)
    12 - isRadar: Radar observations (azimuth, elevation, range, velocity)
    13 - isRanging: Range-only measurements
    14 - isGNSS: GNSS-based position and velocity measurements
    15 - isPosition: Position-only measurements
    16 - isAh: Azimuth and elevation measurements
    17 - isRRD: Range, range-rate, and Doppler measurements
    19 - isOther: Other specialized observation types
    
    Parameters:
    -----------
    ts : str
        Start time in format "YYYY MM DD HH MM SS"
        Example: "2025 01 01 12 00 00"
    step : float
        Time step in seconds for calculations
    te : str
        End time in format "YYYY MM DD HH MM SS"
        Example: "2025 01 02 12 00 00"
    longitude : float
        Observer longitude in degrees (-180 to 180, East positive)
    latitude : float
        Observer latitude in degrees (-90 to 90, North positive)
    altitude : float
        Observer altitude above sea level in meters
    obs_type : int
        Observation type identifier (see Observation Types above)
    min_ele : float
        Minimum elevation angle in degrees (0-90) for valid observations
    solar_distance : float
        Minimum angular distance from Sun in degrees to avoid glare
    lunar_distance : float
        Minimum angular distance from Moon in degrees to avoid interference
    fn_eph : str
        Input satellite ephemeris filename containing orbital data, must use absolute path
    fn_data : str, optional
        Optional output filename for observation data, must use absolute path

    Returns:
    --------
    str: Result message indicating success and observation results

    Examples:
    ---------
    # Angular measurements (azimuth, elevation)
    result = observation_station_satellite(
        ts="2025 01 01 00 00 00",   # Jan 1, 2025 00:00:00 UTC
        step=60.0,                 # 1-minute intervals
        te="2025 01 01 12 00 00",  # 12 hours duration
        longitude=116.4,           # Beijing longitude
        latitude=39.9,             # Beijing latitude
        altitude=50.0,             # 50 meters elevation
        obs_type=11,               # isAlphaDelta - Angular measurements
        min_ele=10.0,              # 10° minimum elevation
        solar_distance=45.0,       # 45° from Sun
        lunar_distance=30.0,       # 30° from Moon
        fn_eph="satellite_eph.txt",
        fn_data="obs_results.txt"
    )
    
    # Radar observation with range and velocity
    result = observation_station_satellite(
        ts="2025 01 01 00 00 00",
        step=30.0,                 # 30-second intervals
        te="2025 01 02 00 00 00",  # 24 hours
        longitude=-74.0,           # New York longitude
        latitude=40.7,             # New York latitude
        altitude=10.0,             # Sea level
        obs_type=12,               # isRadar - Full radar measurements
        min_ele=20.0,              # 20° minimum elevation
        solar_distance=90.0,       # 90° from Sun (night only)
        lunar_distance=45.0,       # 45° from Moon
        fn_eph="target_satellite.eph"
    )
    """
    
    # Convert time strings to MJD format
    def convert_time_format(time_str):
        """Convert 'YYYY MM DD HH MM SS' to 'YYYY-MM-DD HH:MM:SS' format"""
        parts = time_str.strip().split()
        if len(parts) != 6:
            raise ValueError(f"Invalid time format: {time_str}. Expected format: 'YYYY MM DD HH MM SS'")
        
        year, month, day, hour, minute, second = parts
        return f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
    
    try:
        # Convert time strings to date2mjd compatible format
        ts_formatted = convert_time_format(ts)
        te_formatted = convert_time_format(te)
        
        # Convert to MJD using the existing date2mjd function
        from src.dateMJD import date2mjd
        ts_mjd = date2mjd(ts_formatted)
        te_mjd = date2mjd(te_formatted)
        
    except Exception as e:
        return f"Error: Time format conversion failed - {str(e)}"
    
    # Validate input parameters
    if not (-180 <= longitude <= 180):
        return f"Error: Longitude must be between -180 and 180 degrees, got {longitude}"
    
    if not (-90 <= latitude <= 90):
        return f"Error: Latitude must be between -90 and 90 degrees, got {latitude}"
    
    if not (0 <= min_ele <= 90):
        return f"Error: Minimum elevation must be between 0 and 90 degrees, got {min_ele}"
    
    if ts_mjd >= te_mjd:
        return f"Error: Start time ({ts}) must be before end time ({te})"
    
    if step <= 0:
        return f"Error: Time step must be positive, got {step}"
    
    # Validate observation type
    valid_obs_types = [11, 12, 13, 14, 15, 16, 17, 19]
    if obs_type not in valid_obs_types:
        return f"Error: Invalid observation type {obs_type}. Valid types: {valid_obs_types}"
    
    # Call the satellite observation function with MJD values
    from src.observation_station_satellite import run_satellite_observation
    result = run_satellite_observation(
        ts=ts_mjd,
        step=step,
        te=te_mjd,
        longitude=longitude,
        latitude=latitude,
        altitude=altitude,
        obs_type=obs_type,
        min_ele=min_ele,
        solar_distance=solar_distance,
        lunar_distance=lunar_distance,
        fn_eph=fn_eph,
        fn_data=fn_data
    )
    
    return result

# 4 visualization tools
# 4.1 Plot satellite orbit and ground track
@mcp.tool()
def plot_orbit(
    ephemeris_file: str,
    start_time: str,
    end_time: str,
    sat_name: str = 'satellite',
    sat_id: str = 'sat-001',
    orbit_plot: str = 'orbit_plot.png',
    ground_track: str = 'ground_track.png',
    time_step: float = 60.0
) -> str:
    """
    Generate 3D orbit visualization and ground track plots for satellites.
    
    Parameters:
    -----------
    ephemeris_file : str
        Path to ephemeris data file(s). For multiple satellites, separate files with commas.
        must use absolute path
    start_time : str
        Start time for visualization in format "YYYY-MM-DD HH:MM:SS"
    end_time : str
        End time for visualization in format "YYYY-MM-DD HH:MM:SS"
    sat_name : str, optional (default='satellite')
        Satellite name(s). For multiple satellites, separate names with commas.
    sat_id : str, optional (default='sat-001')
        Satellite ID(s). For multiple satellites, separate IDs with commas.
    orbit_plot : str, optional (default='orbit_plot.png')
        Output file path for 3D orbit visualization plot, must use absolute path
    ground_track : str, optional (default='ground_track.png')
        Output file path for ground track plot, must use absolute path
    time_step : float, optional (default=60.0)
        Time step in seconds for plot generation
    
    Returns:
    --------
    str: Status message indicating success and output file locations
    
    Examples:
    ---------
    # Single satellite orbit visualization
    result = plot_orbit(
        ephemeris_file="satellite_eph.txt",
        start_time="2025-01-01 00:00:00",
        end_time="2025-01-01 12:00:00",
        sat_name="ISS",
        sat_id="ISS-001"
    )
    
    # Multiple satellites visualization
    result = plot_orbit(
        ephemeris_file="gps1.txt,gps2.txt",
        start_time="2025-01-01 00:00:00",
        end_time="2025-01-02 00:00:00",
        sat_name="GPS-1,GPS-2",
        sat_id="GPS-001,GPS-002"
    )
    """
    
    try:
        # Call the plot_satellite function
        from src.plot_satellite import plot_satellite
        
        plot_satellite(
            ephemeris_file=ephemeris_file,
            start_time=start_time,
            end_time=end_time,
            sat_name=sat_name,
            sat_id=sat_id,
            orbit_plot=orbit_plot,
            ground_track=ground_track,
            time_step=time_step
        )
        
        return f"Satellite orbit visualization completed successfully. Orbit plot: {orbit_plot}, Ground track: {ground_track}"
        
    except Exception as e:
        return f"Error: Plot generation failed - {str(e)}"
    
# 4.2 satellite access visualization
@mcp.tool()
def plot_access(
    access_file_path: str,
    station_name: str,
    satellite_name: str,
    obs_type: str,
    output_file: str
) -> str:
    """
    Generate visualization plots for satellite observation access data.
    
    This tool reads satellite access data from a file and creates visualization charts
    showing observation parameters like elevation, azimuth, range, etc. over time.
    
    Parameters:
    -----------
    access_file_path : str
        Path to the access data file containing observation data, must use absolute path
    station_name : str
        Name/ID of the ground observation station
    satellite_name : str
        Name/ID of the observed satellite
    obs_type : str
        Observation data type:
        'Azi_Ele': Azimuth and elevation [azimuth(deg), elevation(deg)]
        'RA_DEC': Right ascension and declination [ra(deg), dec(deg)]
        'R_RD': Range and range rate [range(km), range_rate(km/s)]
    output_file : str, optional
        Output file path for the generated plot, must use absolute path
    
    Returns:
    --------
    str: Status message indicating success and output file location
    
    Examples:
    ---------
    # Plot azimuth and elevation access data with default output
    result = plot_access(
        access_file_path="data/beijing_iss_observation.txt",
        station_name="Beijing-001",
        satellite_name="ISS",
        obs_type="Azi_Ele"
    )
    
    # Plot with custom output file path
    result = plot_access(
        access_file_path="data/london_gps_observation.txt",
        station_name="London-002", 
        satellite_name="GPS-001",
        obs_type="RA_DEC",
        output_file="plots/london_gps_radec.png"
    )
    
    # Plot range and range rate data
    result = plot_access(
        access_file_path="data/radar_tracking.txt",
        station_name="Radar-NYC",
        satellite_name="LEO-SAT",
        obs_type="R_RD",
        output_file="results/radar_analysis.png"
    )
    """
    
    # Validate observation type
    valid_obs_types = ['Azi_Ele', 'RA_DEC', 'R_RD']
    if obs_type not in valid_obs_types:
        return f"Error: Invalid observation type '{obs_type}'. Valid types: {valid_obs_types}"
    
    try:
        from src.plot_access import plot_access
        
        plot_result = plot_access(access_file_path, station_name, satellite_name, obs_type, output_file)
        
        # Determine the actual output file path for the return message
        if output_file:
            output_path = output_file
        else:
            output_path = f"figs/{station_name}_{satellite_name}_{obs_type}.png"
        
        # return f"Access data visualization completed successfully. Plot saved to: {output_path}"
        return plot_result
        
    except Exception as e:
        return f"Error: Access plot generation failed - {str(e)}"


# 4.3 ground station visualization
@mcp.tool()
def plot_station(station_data_str: str, output_file: str = None) -> str:
    """
    Generate ground station distribution map showing locations on world map.
    
    This tool creates a world map visualization showing the geographical distribution
    of ground stations with their names and coordinates.
    
    Parameters:
    -----------
    station_data_str : str
        Ground station data string with format: "Name lon lat alt; Name lon lat alt; ..."
        Where:
        - Name: Station name (no spaces)
        - lon: Longitude in degrees (-180 to 180, East positive)
        - lat: Latitude in degrees (-90 to 90, North positive)  
        - alt: Altitude in meters above sea level
        Separate multiple stations with semicolons.
    output_file : str, optional
        Output file path for the generated plot, must use absolute path
    
    Returns:
    --------
    str: Status message indicating success and output file location
    
    Examples:
    ---------
    # Single ground station with default output
    result = plot_station("Beijing 116.4 39.9 50")
    
    # Multiple ground stations with custom output file
    result = plot_station(
        "Beijing 116.4 39.9 50; Tokyo 139.76 35.68 40; NewYork -74.01 40.71 15",
        output_file="plots/global_stations.png"
    )
    
    # Global network of stations
    result = plot_station(
        "Beijing 116.4 39.9 50; Shanghai 121.47 31.23 10; "
        "Tokyo 139.76 35.68 40; Delhi 77.21 28.61 30; "
        "Moscow 37.62 55.75 20; London -0.13 51.51 25; "
        "NewYork -74.01 40.71 15; LosAngeles -118.24 34.05 20; "
        "Sydney 151.21 -33.87 10; CapeTown 18.42 -33.93 20",
        output_file="d:/station_network.png"
    )
    """
    
    try:
        from src.plot_station import plot_station
        
        plot_station(station_data_str, output_file)
        
        # Determine the actual output file path for the return message
        if output_file:
            output_path = output_file
        else:
            output_path = "figs/station_distribution.png"
        
        return f"Ground station distribution plot completed successfully. Plot saved to: {output_path}"
        
    except Exception as e:
        return f"Error: Station plot generation failed - {str(e)}"
    
# 5 initial orbit determination
@mcp.tool()
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
        data_file (str): Path to observation data file (absolute path)
    
    Returns:
        str: Program execution output
    """
    from src.tool_initialOrbitDetermination import initial_orbit_determination as iod_func
    
    try:
        result = iod_func(
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            obs_type=obs_type,
            data_file=data_file
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Start the MCP server
    mcp.run(transport="stdio")
