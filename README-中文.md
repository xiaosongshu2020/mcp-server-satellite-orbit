# MCP Server for Satellite Orbit

一个基于Model Context Protocol (MCP)的卫星轨道计算和可视化服务器。该服务器提供了一系列工具，用于卫星轨道动力学计算、轨道预测、观测数据处理和可视化。

## 功能特性

### 1. 轨道基础工具
- **开普勒根数与笛卡尔坐标转换**：支持开普勒轨道根数与笛卡尔坐标之间的相互转换
- **日期时间转换**：支持日期与修正儒略日(MJD)之间的相互转换

### 2. 轨道预测
- **二体问题轨道预测**：基于经典二体问题动力学的轨道预测
- **高精度数值轨道预测**：使用数值方法进行高精度轨道预测，考虑多种摄动因素

### 3. 卫星观测
- **地面站观测计算**：计算地面站对卫星的观测数据，包括方位角、仰角、距离等

### 4. 可视化工具
- **卫星轨道可视化**：生成3D轨道图和星下点轨迹图
- **观测数据可视化**：绘制卫星观测数据图表
- **地面站分布可视化**：显示地面站地理分布

### 5. 初始轨道确定
- **基于观测数据的轨道确定**：根据地面观测数据计算卫星初始轨道参数

## 安装说明

### 环境要求
- Python 3.13 或更高版本
- Windows操作系统（部分功能依赖Windows exe程序）
- uv包管理工具

### 安装步骤

1. 克隆项目仓库：
   ```bash
   git clone https://github.com/xiaosongshu2020/mcp-server-satellite-orbit.git
   cd mcp-server-satellite-orbit
   ```

2. 使用uv创建虚拟环境并安装依赖：
   ```bash
   uv venv
   uv pip install -e .
   ```

3. 激活虚拟环境：
   ```bash
   # Windows PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .venv\Scripts\Activate.ps1
   
   # Windows Command Prompt
   .venv\Scripts\activate.bat
   ```

## 使用方法

### 启动服务器

有两种方式可以启动服务器：

   ```bash
   uv run run_server.py
   ```

服务器将通过stdio与MCP客户端通信。

### 集成到Claude Desktop

要将此服务器集成到Claude Desktop，请在Claude的配置文件中添加以下JSON配置：

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

请确保将`/path/to/mcp-server-satellite-orbit`替换为项目实际路径。

集成后，您可以在Claude中使用自然语言调用卫星轨道计算工具，例如：
- "将开普勒根数[7000, 0.001, 45, 90, 0, 0]转换为笛卡尔坐标"
- "计算2025年1月1日的简化儒略日"
- "预测卫星轨道，初始时间2025-01-01 00:00:00，初始轨道根数[7000, 0.001, 45, 90, 0, 0]"

### 工具列表

#### 轨道基础工具

1. **kpl2cts** - 开普勒根数转笛卡尔坐标
2. **cts2kpl** - 笛卡尔坐标转开普勒根数
3. **date2mjd** - 日期转修正儒略日
4. **mjd2date** - 修正儒略日转日期

#### 轨道预测工具

1. **orbit_prediction_two_body** - 二体问题轨道预测
2. **orbit_prediction_numerical** - 高精度数值轨道预测

#### 卫星观测工具

1. **observation_station_satellite** - 地面站卫星观测计算

#### 可视化工具

1. **plot_orbit** - 卫星轨道可视化
2. **plot_access** - 卫星观测数据可视化
3. **plot_station** - 地面站分布可视化

#### 初始轨道确定工具

1. **initial_orbit_determination** - 基于观测数据的初始轨道确定

## 项目结构

```
mcp-server-satellite-orbit/
├── bin/                          # 可执行文件目录
│   ├── initialOrbitDetermination.exe
│   ├── observation.exe
│   └── orbitPrediction_numerical.exe
├── data/                         # 数据文件目录
├── OPLIB/                        # 轨道预测库文件
├── src/                          # 源代码目录
│   ├── orbitTools.py             # 轨道基础工具
│   ├── dateMJD.py                # 日期转换工具
│   ├── orbit_prediction_two_body.py  # 二体问题轨道预测
│   ├── observation_station_satellite.py  # 卫星观测计算
│   ├── plot_satellite.py         # 卫星轨道可视化
│   ├── Satellite.py              # 卫星对象类
│   └── ...                       # 其他源文件
├── run_server.py                 # MCP服务器主程序
├── pyproject.toml                # 项目配置文件
└── README.md                     # 项目说明文件
```

## 依赖项

- [mcp](https://github.com/modelcontextprotocol/specification) - Model Context Protocol
- [numpy](https://numpy.org/) - 数值计算库
- [matplotlib](https://matplotlib.org/) - 绘图库
- [cartopy](https://scitools.org.uk/cartopy/docs/latest/) - 地理空间数据处理库
- [astropy](https://www.astropy.org/) - 天体物理学工具库

## 示例

### 简单的轨道转换示例

本项目提供了一个MCP服务器，可以通过MCP客户端调用各种轨道计算工具。用户可以通过客户端发送请求来执行轨道转换、预测和其他操作。

### 轨道预测示例

服务器支持两种轨道预测方法：
1. 基于二体问题的解析方法
2. 考虑多种摄动因素的高精度数值方法

## 许可证

本项目采用MIT许可证。详情请见[LICENSE](LICENSE)文件。
