import datetime
import matplotlib.pyplot as plt
from src.Satellite import Satellite
from src.satelliteScenario import SatelliteScenario
from src.visualize import visualize_orbits, visualize_ground_track

def plot_bds_satellites(start_time, end_time, time_step=60.0):
    """
    绘制24颗BDS卫星的轨道图和星下点轨迹图
    
    参数:
    start_time (str): 开始时间字符串(YYYY-MM-DD HH:MM:SS)
    end_time (str): 结束时间字符串(YYYY-MM-DD HH:MM:SS)
    time_step (float): 时间步长(秒)，默认为60.0
    """
    # 解析时间参数
    if isinstance(start_time, str):
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(end_time, str):
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        
    # 创建场景对象
    scenario = SatelliteScenario(
        name="BDS Satellite Constellation",
        introduction="Visualization of 24 BDS satellites orbit and ground track",
        start_time=start_time,
        end_time=end_time,
        time_step=time_step
    )
    
    # 24颗BDS卫星文件列表
    bds_files = [
        "files/bds_m01_ephemeris.txt",
        "files/bds_m02_ephemeris.txt",
        "files/bds_m03_ephemeris.txt",
        "files/bds_m04_ephemeris.txt",
        "files/bds_m05_ephemeris.txt",
        "files/bds_m06_ephemeris.txt",
        "files/bds_m07_ephemeris.txt",
        "files/bds_m08_ephemeris.txt",
        "files/bds_m09_ephemeris.txt",
        "files/bds_m10_ephemeris.txt",
        "files/bds_m11_ephemeris.txt",
        "files/bds_m12_ephemeris.txt",
        "files/bds_m13_ephemeris.txt",
        "files/bds_m14_ephemeris.txt",
        "files/bds_m15_ephemeris.txt",
        "files/bds_m16_ephemeris.txt",
        "files/bds_m17_ephemeris.txt",
        "files/bds_m18_ephemeris.txt",
        "files/bds_m19_ephemeris.txt",
        "files/bds_m20_ephemeris.txt",
        "files/bds_m21_ephemeris.txt",
        "files/bds_m22_ephemeris.txt",
        "files/bds_m23_ephemeris.txt",
        "files/bds_m24_ephemeris.txt"
    ]
    
    # 添加所有BDS卫星到场景
    for i, eph_file in enumerate(bds_files):
        sat_name = f"BDS-M{i+1:02d}"
        sat_id = f"BDS-{i+1:02d}"
        
        # 创建卫星对象
        satellite = Satellite(name=sat_name, satellite_id=sat_id)
        
        try:
            # 加载星历数据
            satellite.load_ephemeris_data(eph_file)
            satellite.calculate_ground_track()
            
            # 添加卫星到场景
            scenario.add_satellite(satellite)
            print(f"Added {sat_name} from {eph_file}")
            
        except Exception as e:
            print(f"Error loading {eph_file}: {e}")
            continue
    
    # 更新场景时间范围
    scenario.start_time = start_time
    scenario.end_time = end_time

    # 生成轨道图
    orbit_plot = "files/bds_orbit_plot.png"
    print(f"Generating orbit plot: {orbit_plot}")
    fig_orbit, ax_orbit = visualize_orbits(scenario)
    fig_orbit.savefig(orbit_plot, dpi=300, bbox_inches='tight')
    plt.close(fig_orbit)

    # 生成星下点轨迹图
    ground_track = "files/bds_ground_track.png"
    print(f"Generating ground track plot: {ground_track}")
    fig_track, ax_track = visualize_ground_track(scenario)
    fig_track.savefig(ground_track, dpi=300, bbox_inches='tight')
    plt.close(fig_track)

    print("BDS satellite visualization completed successfully")
    print(f"Output files: {orbit_plot}, {ground_track}")

if __name__ == "__main__":
    # 绘制24颗BDS卫星的轨道图和星下点轨迹图
    plot_bds_satellites(
        start_time="2029-05-18 00:00:00",
        end_time="2029-05-22 00:00:00",
        time_step=60.0
    )
