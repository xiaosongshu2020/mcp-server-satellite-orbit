import datetime
import matplotlib.pyplot as plt
from src.Satellite import Satellite
from src.satelliteScenario import SatelliteScenario
from src.visualize import visualize_orbits, visualize_ground_track

def plot_satellite(ephemeris_file, start_time, end_time, sat_name='sat', sat_id='sat-001',
                  orbit_plot='data/orbit_plot.png', ground_track='data/ground_track.png',
                  time_step=60.0):
    """
    绘制卫星轨道和星下点轨迹
    
    参数:
    ephemeris_file (str): 星历数据文件路径(多个文件用逗号分隔)
    start_time (str): 开始时间字符串(YYYY-MM-DD HH:MM:SS)
    end_time (str): 结束时间字符串(YYYY-MM-DD HH:MM:SS)
    sat_name (str): 卫星名称(多个名称用逗号分隔)，默认为'sat'
    sat_id (str): 卫星ID(多个ID用逗号分隔)，默认为'sat-001'
    orbit_plot (str): 轨道图输出路径，默认为'data/orbit_plot.png'
    ground_track (str): 星下点轨迹图输出路径，默认为'data/ground_track.png'
    time_step (float): 时间步长(秒)，默认为60.0
    """
    # 解析时间参数
    if isinstance(start_time, str):
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(end_time, str):
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        
    # 创建场景对象
    scenario = SatelliteScenario(
        name=f"{sat_name} Scenario",
        introduction=f"Visualization of {sat_name} orbit and ground track",
        start_time=start_time,
        end_time=end_time,
        time_step=time_step
    )
    
    # 处理多个卫星文件
    ephemeris_files = [f.strip() for f in ephemeris_file.split(',')]
    sat_names = [f.strip() for f in sat_name.split(',')] if ',' in sat_name else [sat_name]
    sat_ids = [f.strip() for f in sat_id.split(',')] if ',' in sat_id else [sat_id]
    
    # 验证数量匹配
    if len(sat_names) > 1 and len(sat_names) != len(ephemeris_files):
        raise ValueError("sat_name count must match ephemeris_file count")
    if len(sat_ids) > 1 and len(sat_ids) != len(ephemeris_files):
        raise ValueError("sat_id count must match ephemeris_file count")
    
    for i, eph_file in enumerate(ephemeris_files):
        # 创建卫星对象
        name = sat_names[i] if len(sat_names) > 1 else f"{sat_names[0]}-{i+1}"
        sat_id = sat_ids[i] if len(sat_ids) > 1 else f"{sat_ids[0]}-{i+1}"
        satellite = Satellite(name=name, satellite_id=sat_id)
        
        # 加载星历数据
        satellite.load_ephemeris_data(eph_file)
        satellite.calculate_ground_track()
        
        # 添加卫星到场景
        scenario.add_satellite(satellite)
        
    # 更新场景时间范围
    scenario.start_time = start_time
    scenario.end_time = end_time

    # 生成轨道图
    print(f"Generating orbit plot: {orbit_plot}")
    fig_orbit, ax_orbit = visualize_orbits(scenario)
    fig_orbit.savefig(orbit_plot, dpi=300, bbox_inches='tight')
    plt.close(fig_orbit)

    # 生成星下点轨迹图
    print(f"Generating ground track plot: {ground_track}")
    fig_track, ax_track = visualize_ground_track(scenario)
    fig_track.savefig(ground_track, dpi=300, bbox_inches='tight')
    plt.close(fig_track)

    print("Visualization completed successfully")

if __name__ == "__main__":
    # 示例用法 - 单个卫星
    plot_satellite(
        ephemeris_file="iss_high_precision_eph.txt",
        start_time="2025-01-01 00:00:00",
        end_time="2025-01-02 00:00:00",
        sat_name="My Satellite",
        sat_id="SAT-001",
        orbit_plot="my_orbit.png",
        ground_track="my_ground_track.png"
    )
    
    # 示例用法 - 多个卫星
    plot_satellite(
        ephemeris_file="ephemeris_LEO-001.txt,ephemeris_GPS-001.txt",
        start_time="2025-01-01 00:00:00",
        end_time="2025-01-02 00:00:00",
        sat_name="LEO Satellite,GPS Satellite",
        sat_id="SAT-LEO-001,SAT-GPS-001",
        orbit_plot="multi_orbit.png",
        ground_track="multi_ground_track.png"
    )
