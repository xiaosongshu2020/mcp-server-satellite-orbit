# MCP Server for Satellite Orbit

A Model Context Protocol (MCP) based satellite orbit calculation and visualization server. This server provides a suite of tools for satellite orbital dynamics calculations, orbit prediction, observation data processing, and visualization.

## Features

### 1. Orbital Basic Tools
- **Keplerian Elements and Cartesian Coordinates Conversion**: Support for mutual conversion between Keplerian orbital elements and Cartesian coordinates
- **Date Time Conversion**: Support for mutual conversion between date and Modified Julian Date (MJD)

### 2. Orbit Prediction
- **Two-Body Problem Orbit Prediction**: Orbit prediction based on classical two-body problem dynamics
- **High-Precision Numerical Orbit Prediction**: High-precision orbit prediction using numerical methods, considering multiple perturbation factors

### 3. Satellite Observation
- **Ground Station Observation Calculation**: Calculate observation data for satellites from ground stations, including azimuth, elevation, range, etc.

### 4. Visualization Tools
- **Satellite Orbit Visualization**: Generate 3D orbit plots and ground track plots
- **Observation Data Visualization**: Plot satellite observation data charts
- **Ground Station Distribution Visualization**: Display ground station geographical distribution

### 5. Initial Orbit Determination
- **Orbit Determination Based on Observation Data**: Calculate satellite initial orbit parameters based on ground observation data

## Installation Instructions

### Environment Requirements
- Python 3.13 or higher
- Windows operating system (some features depend on Windows exe programs)
- uv package manager

### Installation Steps

1. Clone the project repository:
   ```bash
   git clone https://github.com/xiaosongshu2020/mcp-server-satellite-orbit.git
   cd mcp-server-satellite-orbit
   ```

2. Use uv to create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   ```

3. Activate the virtual environment:
   ```bash
   # Windows PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .venv\Scripts\Activate.ps1
   
   # Windows Command Prompt
   .venv\Scripts\activate.bat
   ```

## Usage

### Starting the Server

There are two ways to start the server:

   ```bash
   uv run run_server.py
   ```

The server will communicate with MCP clients through stdio.

### Integration with Claude Desktop

To integrate this server with Claude Desktop, add the following JSON configuration to Claude's configuration file:

```json
{
  "mcpServers": {
    "mcp-server-satOrbit":{
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-server-satellite-orbit",
        "run",
        "run_server.py"
      ]
    }
  }
}
```

Please ensure to replace `/path/to/mcp-server-satellite-orbit` with the actual project path.

After integration, you can use natural language in Claude to call satellite orbit calculation tools, such as:
- "Convert Keplerian elements [7000, 0.001, 45, 90, 0, 0] to Cartesian coordinates"
- "Calculate the Modified Julian Date for January 1, 2025"
- "Predict satellite orbit, initial time 2025-01-01 00:00:00, initial orbital elements [7000, 0.001, 45, 90, 0, 0]"

### Tool List

#### Orbital Basic Tools

1. **kpl2cts** - Keplerian elements to Cartesian coordinates
2. **cts2kpl** - Cartesian coordinates to Keplerian elements
3. **date2mjd** - Date to Modified Julian Date
4. **mjd2date** - Modified Julian Date to date

#### Orbit Prediction Tools

1. **orbit_prediction_two_body** - Two-body problem orbit prediction
2. **orbit_prediction_numerical** - High-precision numerical orbit prediction

#### Satellite Observation Tools

1. **observation_station_satellite** - Ground station satellite observation calculation

#### Visualization Tools

1. **plot_orbit** - Satellite orbit visualization
2. **plot_access** - Satellite observation data visualization
3. **plot_station** - Ground station distribution visualization

#### Initial Orbit Determination Tools

1. **initial_orbit_determination** - Initial orbit determination based on observation data

## Project Structure

```
mcp-server-satellite-orbit/
├── bin/                          # Executable files directory
│   ├── initialOrbitDetermination.exe
│   ├── observation.exe
│   └── orbitPrediction_numerical.exe
├── data/                         # Data files directory
├── OPLIB/                        # Orbit prediction library files
├── src/                          # Source code directory
│   ├── orbitTools.py             # Orbital basic tools
│   ├── dateMJD.py                # Date conversion tools
│   ├── orbit_prediction_two_body.py  # Two-body problem orbit prediction
│   ├── observation_station_satellite.py  # Satellite observation calculation
│   ├── plot_satellite.py         # Satellite orbit visualization
│   ├── Satellite.py              # Satellite object class
│   └── ...                       # Other source files
├── run_server.py                 # MCP server main program
├── pyproject.toml                # Project configuration file
└── README.md                     # Project documentation file
```

## Dependencies

- [mcp](https://github.com/modelcontextprotocol/specification) - Model Context Protocol
- [numpy](https://numpy.org/) - Numerical computing library
- [matplotlib](https://matplotlib.org/) - Plotting library
- [cartopy](https://scitools.org.uk/cartopy/docs/latest/) - Geospatial data processing library
- [astropy](https://www.astropy.org/) - Astrophysics tools library

## Examples

### Simple Orbit Conversion Example

This project provides an MCP server that can call various orbit calculation tools through MCP clients. Users can send requests through the client to perform orbit conversion, prediction, and other operations.

### Orbit Prediction Example

The server supports two orbit prediction methods:
1. Analytical method based on the two-body problem
2. High-precision numerical method considering multiple perturbation factors

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
