# 1.3 convert date to Modified Julian date
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
    from datetime import datetime
    
    # Parse the date string
    if len(date) == 10:  # YYYY-MM-DD format
        dt = datetime.strptime(date, "%Y-%m-%d")
    else:  # YYYY-MM-DD HH:MM:SS format
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    
    year = float(dt.year)
    month = float(dt.month)
    day = float(dt.day)
    hour = dt.hour
    minute = dt.minute
    second = dt.second
    
    # Convert time to seconds since midnight
    sec = hour * 3600 + minute * 60 + second
    
    # Implementation based on the Fortran date2MJD subroutine
    y = year
    m = month
    b = 0.0
    c = 0.0
    
    if m <= 2:
        y = y - 1.0
        m = m + 12.0
    
    if y < 0:
        c = -0.75
    
    # Check for valid calendar date (Gregorian calendar reform)
    if year < 1582:
        pass
    elif year > 1582:
        a = int(y / 100.0)
        b = 2.0 - a + int(a / 4.0)
    elif month < 10:
        pass
    elif month > 10:
        a = int(y / 100.0)
        b = 2.0 - a + int(a / 4.0)
    elif day <= 4:
        pass
    elif day > 14:
        a = int(y / 100.0)
        b = 2.0 - a + int(a / 4.0)
    else:
        raise ValueError("Invalid calendar date during Gregorian calendar reform period (Oct 5-14, 1582)")
    
    jd_tmp = int(365.25 * y + c) + int(30.6001 * (m + 1))
    mjd_day = jd_tmp + day + b - 679006.0
    mjd_sec = sec
    
    # Convert to single MJD value (day + fraction)
    mjd = mjd_day + mjd_sec / 86400.0
    
    return mjd


# 1.4 convert Modified Julian date to date
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
    jd = mjd + 2400000.5
    
    # Split Julian Date into integer and fractional parts
    jd_int = int(jd + 0.5)
    jd_frac = jd + 0.5 - jd_int
    
    # Ensure fraction is in range [0, 1)
    if jd_frac < 0:
        jd_frac += 1.0
        jd_int -= 1
    elif jd_frac >= 1.0:
        jd_frac -= 1.0
        jd_int += 1
    
    # Implementation based on the Fortran JD2date subroutine
    # Convert Julian Date to Gregorian calendar date
    l = jd_int + 68569
    n = (4 * l) // 146097
    l = l - (146097 * n + 3) // 4
    i = (4000 * (l + 1)) // 1461001
    l = l - (1461 * i) // 4 + 31
    k = (80 * l) // 2447
    day = l - (2447 * k) // 80
    l = k // 11
    month = k + 2 - 12 * l
    year = 100 * (n - 49) + i + l
    
    # Convert fractional day to hours, minutes, seconds
    total_seconds = jd_frac * 86400.0
    hour = int(total_seconds // 3600)
    minute = int((total_seconds % 3600) // 60)
    second = int(total_seconds % 60)
    
    # Handle rounding errors that might cause seconds to be 60
    if second >= 60:
        second = 0
        minute += 1
    if minute >= 60:
        minute = 0
        hour += 1
    if hour >= 24:
        hour = 0
        # Would need to add a day, but this should be rare due to our fraction handling
    
    # Format as string
    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

if __name__ == "__main__":
    # Test the functions
    print(date2mjd("2000-01-01 00:00:00"))
    print(mjd2date(51544.0))