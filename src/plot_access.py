import os
from access import Access
from visualize import visualize_access

def plot_access(access_file_path, station_name, satellite_name, obs_type, output_file=None):
    """
    读取访问数据文件并绘制可视化图表
    
    参数:
    access_file_path (str): 访问数据文件路径
    station_name (str): 观测站名称/ID
    satellite_name (str): 卫星名称/ID
    obs_type (str): 观测数据类型
                   'Azi_Ele': 方位角俯仰角 [azimuth(deg), elevation(deg)]
                   'RA_DEC': 赤经赤纬 [ra(deg), dec(deg)]
                   'R_RD': 测距测速 [range(km), range_rate(km/s)]
    output_file (str, optional): 输出图片文件路径。如果未指定，默认为 
                                "figs/{station_name}_{satellite_name}_{obs_type}.png"
    """
    
    # 验证观测类型
    valid_obs_types = ['Azi_Ele', 'RA_DEC', 'R_RD']
    if obs_type not in valid_obs_types:
        print(f"错误: 无效的观测类型 '{obs_type}'. 有效类型: {valid_obs_types}")
        return f"错误: 无效的观测类型 '{obs_type}'. 有效类型: {valid_obs_types}"
    
    # 检查文件是否存在
    if not os.path.exists(access_file_path):
        print(f"错误: 访问数据文件不存在: {access_file_path}")
        return f"错误: 访问数据文件不存在: {access_file_path}"
    
    # 创建Access对象
    access_obj = Access(station_name, satellite_name, obs_type)
    
    # 读取数据文件
    access_obj.read_observation_data(access_file_path)
    
    if len(access_obj.data) == 0:
        print(f"警告: 没有可用的观测数据 - {access_file_path}")
        return f"警告: 没有可用的观测数据 - {access_file_path}"
    
    # 可视化数据
    fig, axes = visualize_access(access_obj)
    
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
            output_filename = f"{output_dir}/{station_name}_{satellite_name}_{obs_type}.png"
        
        fig.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"可视化图表已保存到: {output_filename}")

        # 导入matplotlib.pyplot并关闭图形
        import matplotlib.pyplot as plt
        plt.close(fig)

        return f"可视化图表已保存到: {output_filename}"

def main():
    """
    主函数 - 处理示例访问数据文件
    """
    # 示例数据处理
    test_cases = [
        {
            "file": "data/beijing_iss_observation.txt",
            "station": "Beijing-001",
            "satellite": "ISS",
            "obs_type": "Azi_Ele",
            "output": "plots/beijing_iss_aziele.png"
        },
        {
            "file": "data/london_gps_observation.txt", 
            "station": "London-002",
            "satellite": "GPS-001",
            "obs_type": "RA_DEC",
            "output": "plots/london_gps_radec.png"
        },
        {
            "file": "data/radar_tracking.txt",
            "station": "Radar-NYC",
            "satellite": "LEO-SAT",
            "obs_type": "R_RD",
            "output": None  # 使用默认路径
        }
    ]
    
    for case in test_cases:
        print(f"\n处理观测数据:")
        print(f"  文件: {case['file']}")
        print(f"  观测站: {case['station']}")
        print(f"  卫星: {case['satellite']}")
        print(f"  观测类型: {case['obs_type']}")
        print(f"  输出文件: {case['output'] if case['output'] else '默认路径'}")
        
        plot_access(
            access_file_path=case['file'],
            station_name=case['station'],
            satellite_name=case['satellite'],
            obs_type=case['obs_type'],
            output_file=case['output']
        )

if __name__ == "__main__":
    main()