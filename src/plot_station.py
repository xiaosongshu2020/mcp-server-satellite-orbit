import os
import matplotlib.pyplot as plt
from Station import GroundStation
from visualize import visualize_stations

class SimpleScenario:
    """简单的场景类，仅包含地面站列表"""
    def __init__(self, ground_stations):
        self.ground_stations = ground_stations
        self.name = "Ground Stations Distribution"
        self.introduction = "Visualization of ground stations"

def plot_station(station_data_str, output_file=None):
    """
    绘制地面站分布图
    
    参数:
    station_data_str (str): 地面站数据字符串，格式为"Name lon lat alt; Name lon lat alt; ..."
    output_file (str, optional): 输出图片文件路径。如果未指定，默认为 "figs/station_distribution.png"
    """
    # 解析地面站数据
    stations = []
    station_id = 1  # 为每个站分配一个ID
    
    for station_str in station_data_str.split(';'):
        station_str = station_str.strip()
        if not station_str:
            continue
            
        try:
            parts = station_str.split()
            if len(parts) != 4:
                print(f"警告: 跳过格式不正确的地面站数据: {station_str}")
                continue
                
            name = parts[0]
            lon = float(parts[1])
            lat = float(parts[2])
            alt = float(parts[3])
            
            # 创建地面站对象
            station = GroundStation(
                name=name,
                station_id=f"STN-{station_id:03d}",
                longitude=lon,
                latitude=lat,
                altitude=alt
            )
            stations.append(station)
            station_id += 1
            
        except ValueError as e:
            print(f"错误: 解析地面站数据失败 - {station_str}: {e}")
            continue
    
    if not stations:
        print("错误: 没有有效的地面站数据")
        return
    
    # 创建简单场景对象并绘制分布图
    scenario = SimpleScenario(stations)
    fig, ax = visualize_stations(scenario, projection='PlateCarree')
    
    if fig is not None:
        # 确定输出文件路径
        if output_file:
            output_filename = output_file
            # 创建输出目录（如果需要）
            output_dir = os.path.dirname(output_filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
        else:
            # 使用默认路径
            output_dir = "figs"
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{output_dir}/station_distribution.png"
        
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"地面站分布图已保存到: {output_filename}")
        plt.close(fig)

if __name__ == "__main__":
    # 全球分布的20个地面站示例
    global_stations = """
        Beijing 116.4 39.9 50; Shanghai 121.47 31.23 10; 
        Tokyo 139.76 35.68 40; Delhi 77.21 28.61 30;
        Moscow 37.62 55.75 20; London -0.13 51.51 25;
        NewYork -74.01 40.71 15; LosAngeles -118.24 34.05 20;
        Sydney 151.21 -33.87 10; Rio -43.17 -22.91 30;
        CapeTown 18.42 -33.93 20; Nairobi 36.82 -1.29 15;
        Dubai 55.27 25.20 50; Singapore 103.85 1.30 10;
        Honolulu -157.86 21.31 5; Anchorage -149.90 61.22 10;
        Reykjavik -21.94 64.15 5; Auckland 174.76 -36.85 15;
        Santiago -70.67 -33.45 20; Vancouver -123.12 49.28 10
    """
    
    # 测试默认输出路径
    print("测试1: 默认输出路径")
    plot_station(global_stations)
    
    # 测试自定义输出路径
    print("\n测试2: 自定义输出路径")
    plot_station(
        "Beijing 116.4 39.9 50; Tokyo 139.76 35.68 40; NewYork -74.01 40.71 15",
        output_file="plots/custom_stations.png"
    )