import numpy as np

#######################################################################################
class ModuleConst:
    """
    Python implementation of the Fortran module_const module containing various physical constants
    and parameter definitions for space applications.
    """
    
    # Units
    length_unit = 6378.1363                     # km
    time_unit = 806.81099130673260              # s
    mass_unit = 5.9742272407074334e24           # kg
    acc_unit = 9.79828762253515                 # m/s^2
    force_unit = 5.853719682683597e25           # N
    
    # GGM03C, EGM96
    R_Earth = 6378.1363                         # km
    f_Earth = 1.0/298.256415
    # WGS84 parameters (commented out in original)
    # R_Earth = 6378.137                        # km
    # f_Earth = 1.0/298.257223563
    
    # cislunar normalized units/地月空间归一化单位
    mass_Earth = 5.9742272407074334e24          # 地球质量，kg
    mass_Moon = 7.34832238736047e22             # 月球质量, kg
    MER = 0.0121505856313668                    # 月球质量/地月质量和
    MUc = 6.04771046458104e24                   # 质量单位，地月质量和，kg
    LUc = 384401000.0                           # 长度单位，地月平均距离，m
    TUc = 375163.609176656                      # 时间单位，s，约4.34天
    
    # Angles
    pi = np.pi
    deg2rad = np.pi/180.0
    rad2deg = 180.0/np.pi
    sec2rad = 4.84813681109536e-6
    rad2sec = 206264.806247096
    
    # Basic constants
    c_const = 299792458.0                       # m/s
    c_unit = 3.792265308366992e4                # Ae/T
    AU = 1.49597870e8                           # km
    AUstd = 1.49597870e8/6378.1363              # AU -> Ae
    J2const = 1.082629989e-3
    GC = 6.673e-11                              # Gravity Constant, m^3/(kg/s^2)
    
    # Types of satellite's states
    isKeplerian = 1
    isCartesian = 2
    isNSG1 = 3                                  # First kind of non-singular elements
    isNSG2 = 4                                  # Second kind of non-singular elements
    
    # Types of observational data or access
    isAlphaDelta = 11                           # Angles
    isRadar = 12                                # A, h, range and velocity
    isRanging = 13                              # range
    isGNSS = 14                                 # position and velocity
    isPosition = 15                             # position
    isAh = 16                                   # A, h
    isRRD = 17                                  # range and velocity
    isOther = 19
    
    # Types of orbit determination method
    useBatchProcess = 1001
    useEKF = 1002
    useUKF = 1003
    
    # Types of object
    isStation = 101
    isSatellite = 102
    
    # Types of time
    isUTC = 1
    isTDT = 2
    isUT1 = 3
    isBDT = 4
    isGPST = 5

#######################################################################################
def kpl2cts(elements):
    """
    Convert Keplerian elements to Cartesian coordinates
    
    Parameters:
    elements (array-like): Array of 6 Keplerian elements
        elements[0]: a - semi-major axis (km)
        elements[1]: e - eccentricity
        elements[2]: i - inclination (degrees)
        elements[3]: C_omega - longitude of ascending node (uppercase omega/Ω) (degrees)
        elements[4]: omega - argument of periapsis (lowercase omega/ω) (degrees)
        elements[5]: M - mean anomaly (degrees)
    
    Returns:
    numpy.ndarray: Array of 6 Cartesian elements [x, y, z, vx, vy, vz] (km, km/s)
    """
    # Make a copy to avoid modifying the original input
    elements = np.array(elements, dtype=float)
    
    # Constants
    pi_constant = np.pi

    elements[0] = elements[0] / ModuleConst.length_unit
    elements[2:6] = elements[2:6] * ModuleConst.deg2rad  # Convert degrees to radians
    
    # Extract Keplerian elements
    a = elements[0]
    e_element = elements[1]
    i = elements[2]
    C_omega = elements[3]
    omega = elements[4]
    M = elements[5]
    
    # Calculate P and Q vectors
    P = np.zeros(3)
    Q = np.zeros(3)
    
    P[0] = np.cos(C_omega) * np.cos(omega) - np.sin(C_omega) * np.sin(omega) * np.cos(i)
    P[1] = np.sin(C_omega) * np.cos(omega) + np.cos(C_omega) * np.sin(omega) * np.cos(i)
    P[2] = np.sin(omega) * np.sin(i)
    
    Q[0] = -np.cos(C_omega) * np.sin(omega) - np.sin(C_omega) * np.cos(omega) * np.cos(i)
    Q[1] = -np.sin(C_omega) * np.sin(omega) + np.cos(C_omega) * np.cos(omega) * np.cos(i)
    Q[2] = np.cos(omega) * np.sin(i)
    
    # Solve Kepler's equation iteratively
    M_mod = M % (2 * pi_constant)
    E = M_mod
    
    # Use more iterations for better accuracy
    for _ in range(10):
        E_new = E - (E - e_element * np.sin(E) - M_mod) / (1 - e_element * np.cos(E))
        if abs(E_new - E) < 1e-12:
            break
        E = E_new
    
    # Calculate position vector
    r = a * (np.cos(E) - e_element) * P + a * np.sqrt(1.0 - e_element**2) * np.sin(E) * Q
    r_norm = np.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
    
    # Calculate velocity vector
    v = np.sqrt(a) / r_norm * (-np.sin(E) * P + np.sqrt(1.0 - e_element**2) * np.cos(E) * Q)
    
    # Combine position and velocity into Cartesian elements
    cts = np.zeros(6)
    cts[0:3] = r * ModuleConst.length_unit  # Convert to km
    cts[3:6] = v * ModuleConst.length_unit / ModuleConst.time_unit  # Convert to km/s
    
    return cts

#######################################################################################
def cts2kpl(rv):
    """
    Convert Cartesian coordinates to Keplerian elements
    
    Parameters:
    rv (array-like): Array of 6 Cartesian elements [x, y, z, vx, vy, vz] (km, km/s)
    
    Returns:
    numpy.ndarray: Array of 6 Keplerian elements
        [a, e, i, C_omega, omega, M]
        a - semi-major axis (km)
        e - eccentricity
        i - inclination (degrees)
        C_omega - longitude of ascending node (uppercase omega/Ω) (degrees)
        omega - argument of periapsis (lowercase omega/ω) (degrees)
        M - mean anomaly (degrees)
    """
    # Make a copy to avoid modifying the original input
    rv = np.array(rv, dtype=float)
    
    # Extract position and velocity vectors
    r = rv[0:3] / ModuleConst.length_unit  
    v = rv[3:6] * ModuleConst.time_unit / ModuleConst.length_unit 
    
    # Set gravitational parameter (mu)
    miu = 1.0
    
    # Calculate norms
    v_norm = np.linalg.norm(v)
    r_norm = np.linalg.norm(r)
    
    # Calculate semi-major axis
    a = 1.0 / (2.0 / r_norm - v_norm**2 / miu)
    
    # Calculate eccentricity
    e_element = np.sqrt((1.0 - r_norm / a)**2 + 
                       (np.dot(r, v) / np.sqrt(miu * a))**2)
    
    # Calculate eccentric anomaly
    E = np.arctan2(np.dot(r, v) / np.sqrt(miu * a), 1.0 - r_norm / a)
    
    # Calculate true anomaly
    f = np.arctan2(np.sqrt(1.0 - e_element**2) * np.sin(E), np.cos(E) - e_element)
    
    # Calculate mean anomaly
    M = E - e_element * np.sin(E)
    
    # Ensure M is in [0, 2π] range
    M = M % (2 * np.pi)
    
    # Calculate P and Q vectors
    P = np.cos(E) / r_norm * r - np.sqrt(a / miu) * np.sin(E) * v
    Q = (1.0 - e_element**2)**(-0.5) * (np.sin(E) / r_norm * r + 
         np.sqrt(a / miu) * (np.cos(E) - e_element) * v)
    
    # Calculate angular momentum vector
    R_array = np.zeros(3)
    R_array[0] = r[1] * v[2] - r[2] * v[1]
    R_array[1] = r[2] * v[0] - r[0] * v[2]
    R_array[2] = r[0] * v[1] - r[1] * v[0]
    R_array = R_array / np.sqrt(miu * a * (1.0 - e_element**2))
    
    # Calculate angular elements
    omega = np.arctan2(P[2], Q[2])
    C_omega = np.arctan2(R_array[0], -R_array[1])
    i = np.arccos(np.clip(R_array[2], -1.0, 1.0))  # Clip to avoid numerical errors
    
    # Ensure angles are in [0, 2π] range
    omega = omega % (2 * np.pi)
    C_omega = C_omega % (2 * np.pi)
    
    # Return Keplerian elements
    elements = np.array([a, e_element, i, C_omega, omega, M])

    elements[0] = elements[0] * ModuleConst.length_unit  # Convert to km
    elements[2:6] = elements[2:6] * ModuleConst.rad2deg  # Convert radians to degrees

    return elements

#######################################################################################

if __name__ == "__main__":
    # Example usage and testing
    print("Testing orbital element conversions...")
    
    # Test case 1: Circular orbit
    keplerian_elements = np.array([7000, 0.0, 0, 0, 0, 0])
    print("\nTest 1 - Circular equatorial orbit:")
    print("Original Keplerian Elements:", keplerian_elements)
    
    cartesian_elements = kpl2cts(keplerian_elements)
    print("Cartesian Elements:", cartesian_elements)
    
    converted_keplerian_elements = cts2kpl(cartesian_elements)
    print("Converted back to Keplerian:", converted_keplerian_elements)
    
    # Test case 2: Elliptical inclined orbit
    keplerian_elements2 = np.array([7000, 0.1, 45, 90, 30, 0])
    print("\nTest 2 - Elliptical inclined orbit:")
    print("Original Keplerian Elements:", keplerian_elements2)
    
    cartesian_elements2 = kpl2cts(keplerian_elements2)
    print("Cartesian Elements:", cartesian_elements2)
    
    converted_keplerian_elements2 = cts2kpl(cartesian_elements2)
    print("Converted back to Keplerian:", converted_keplerian_elements2)
    
    # Check conversion accuracy
    diff = np.abs(keplerian_elements2 - converted_keplerian_elements2)
    print("Conversion differences:", diff)
    print("Max difference:", np.max(diff))