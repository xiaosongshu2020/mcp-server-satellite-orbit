import datetime
import matplotlib.pyplot as plt
import os

from satelliteScenario import SatelliteScenario
from Satellite import Satellite
from Station import GroundStation
from access import Access
import visualize

def demo1_satellite_orbits():
    """
    Demo1：卫星轨道演示
    - 创建satelliteScenario
    - 添加三颗卫星
    - 计算星历，保存到data/目录
    - 画3D轨道图
    - 画星下点轨迹
    """
    print("=" * 80)
    print("Demo1: 卫星轨道演示")
    print("=" * 80)
    
    # 设置时间参数
    start_time = datetime.datetime(2023, 10, 1, 0, 0, 0)
    end_time = start_time + datetime.timedelta(hours=12)
    time_step = 120  # 2分钟步长
    
    # 创建场景
    scenario = SatelliteScenario(
        name="Three Satellites Orbit Demo",
        introduction="Demonstration of three satellites with different orbital elements",
        start_time=start_time,
        end_time=end_time,
        time_step=time_step
    )
    
    # 创建三颗不同轨道的卫星
    satellites = [
        Satellite(
            name="GPS Satellite",
            satellite_id="GPS-001",
            initial_kepler_elements={
                'a': 26578.0,  # GPS轨道
                'e': 0.01,
                'i': 55.0,
                'Omega': 100.0,
                'omega': 0.0,
                'M0': 0.0
            }
        ),
        Satellite(
            name="LEO Satellite", 
            satellite_id="LEO-001",
            initial_kepler_elements={
                'a': 7000.0,  # LEO轨道
                'e': 0.001,
                'i': 98.0,   # 太阳同步轨道倾角
                'Omega': 0.0,
                'omega': 0.0,
                'M0': 0.0
            }
        ),
        Satellite(
            name="GEO Satellite",
            satellite_id="GEO-001", 
            initial_kepler_elements={
                'a': 42164.0,  # 地球同步轨道
                'e': 0.0,
                'i': 0.0,      # 赤道轨道
                'Omega': 0.0,
                'omega': 0.0,
                'M0': 0.0
            }
        )
    ]
    
    # 添加卫星到场景
    for sat in satellites:
        scenario.add_satellite(sat)
    
    print(f"已创建场景包含 {len(scenario.satellites)} 颗卫星:")
    for sat in scenario.satellites:
        print(f"  - {sat.name} ({sat.satellite_id})")
    
    # 计算轨道
    print("\n正在计算卫星轨道...")
    scenario.propagate_all_orbits()
    
    # 保存星历数据到data目录
    print("\n正在保存星历数据...")
    scenario.save_all_satellite_ephemeris("data")
    
    # 计算星下点轨迹（只为第一颗卫星）
    print("\n正在计算星下点轨迹...")
    scenario.satellites[0].calculate_ground_track()
    
    # 可视化3D轨道
    print("\n正在生成3D轨道图...")
    fig_orbits, ax_orbits = visualize.visualize_orbits(scenario)
    plt.show()
    try:
        os.makedirs("figs", exist_ok=True)
        fig_orbits.savefig("figs/demo1_satellite_orbits.png", dpi=300, bbox_inches='tight')
        print("3D轨道图已保存到 figs/demo1_satellite_orbits.png")
    except Exception as e:
        print(f"保存3D轨道图失败: {e}")
    
    # 可视化星下点轨迹
    print("\n正在生成星下点轨迹图...")
    fig_track, ax_track = visualize.visualize_ground_track(scenario)
    plt.show()
    try:
        fig_track.savefig("figs/demo1_ground_track.png", dpi=300, bbox_inches='tight')
        print("星下点轨迹图已保存到 figs/demo1_ground_track.png")
    except Exception as e:
        print(f"保存星下点轨迹图失败: {e}")
    
    print("\nDemo1 完成！")
    return scenario


def demo2_satellite_observation():
    """
    Demo2：卫星观测演示
    - 创建satelliteScenario
    - 添加3个观测站，添加1颗卫星
    - 创建access，三个测站分别观测Azi_Ele, RA_DEC, R_RD
    - 画3D轨道图
    - 画星下点轨迹
    - 画测站分布图
    - 计算access
    - 画access数据
    """
    print("=" * 80)
    print("Demo2: 卫星观测演示")
    print("=" * 80)
    
    # 设置时间参数
    start_time = datetime.datetime(2023, 10, 1, 0, 0, 0)
    end_time = start_time + datetime.timedelta(hours=6)
    time_step = 60  # 1分钟步长
    
    # 创建场景
    scenario = SatelliteScenario(
        name="Satellite Observation Demo",
        introduction="Demonstration of satellite observation from multiple ground stations",
        start_time=start_time,
        end_time=end_time,
        time_step=time_step
    )
    
    # 创建三个地面站
    ground_stations = [
        GroundStation(
            name="Beijing Station",
            station_id="BJ-001",
            longitude=116.3,
            latitude=39.9,
            altitude=44
        ),
        GroundStation(
            name="London Station", 
            station_id="LDN-002",
            longitude=-0.1,
            latitude=51.5,
            altitude=25
        ),
        GroundStation(
            name="Sydney Station",
            station_id="SYD-003",
            longitude=151.2,
            latitude=-33.9,
            altitude=58
        )
    ]
    
    # 添加地面站到场景
    for station in ground_stations:
        scenario.add_ground_station(station)
    
    # 创建一颗卫星
    satellite = Satellite(
        name="Observation Target",
        satellite_id="OBS-SAT-001",
        initial_kepler_elements={
            'a': 7200.0,   # LEO轨道
            'e': 0.001,
            'i': 45.0,     # 中等倾角，便于多个地面站观测
            'Omega': 100.0,
            'omega': 0.0,
            'M0': 0.0
        }
    )
    
    scenario.add_satellite(satellite)
    
    print(f"已创建场景包含:")
    print(f"  - {len(scenario.ground_stations)} 个地面站")
    print(f"  - {len(scenario.satellites)} 颗卫星")
    
    # 创建不同类型的观测对象
    obs_configs = [
        ("BJ-001", "OBS-SAT-001", "Azi_Ele"),
        ("LDN-002", "OBS-SAT-001", "RA_DEC"), 
        ("SYD-003", "OBS-SAT-001", "R_RD")
    ]
    
    print(f"\n正在创建 {len(obs_configs)} 个观测对象...")
    created_accesses = []
    for station_id, sat_id, obs_type in obs_configs:
        access = scenario.create_access(station_id, sat_id, obs_type)
        created_accesses.append(access)
        print(f"  - {station_id} → {sat_id} ({obs_type})")
    
    # 计算轨道
    print("\n正在计算卫星轨道...")
    scenario.propagate_all_orbits()
    
    # 计算星下点轨迹
    print("正在计算星下点轨迹...")
    scenario.satellites[0].calculate_ground_track()
    
    # 可视化3D轨道
    print("\n正在生成3D轨道图...")
    fig_orbits, ax_orbits = visualize.visualize_orbits(scenario)
    plt.show()
    try:
        os.makedirs("figs", exist_ok=True)
        fig_orbits.savefig("figs/demo2_satellite_orbits.png", dpi=300, bbox_inches='tight')
        print("3D轨道图已保存到 figs/demo2_satellite_orbits.png")
    except Exception as e:
        print(f"保存3D轨道图失败: {e}")
    
    # 可视化星下点轨迹  
    print("\n正在生成星下点轨迹图...")
    fig_track, ax_track = visualize.visualize_ground_track(scenario)
    plt.show()
    try:
        fig_track.savefig("figs/demo2_ground_track.png", dpi=300, bbox_inches='tight')
        print("星下点轨迹图已保存到 figs/demo2_ground_track.png")
    except Exception as e:
        print(f"保存星下点轨迹图失败: {e}")
    
    # 可视化地面站分布
    print("\n正在生成地面站分布图...")
    fig_stations, ax_stations = visualize.visualize_stations(
        scenario,
        show_altitude=True,
        altitude_colormap='viridis',
        size_by_altitude=True,
        station_size=200
    )
    plt.show()
    try:
        fig_stations.savefig("figs/demo2_ground_stations.png", dpi=300, bbox_inches='tight')
        print("地面站分布图已保存到 figs/demo2_ground_stations.png")
    except Exception as e:
        print(f"保存地面站分布图失败: {e}")
    
    # 计算观测数据
    print("\n正在计算观测数据...")
    scenario.calculate_all_accesses(elevation_mask=10.0)
    
    # 保存观测数据
    print("\n正在保存观测数据...")
    scenario.save_all_access_data("data/access_data")
    
    # 可视化所有access的观测数据
    print("\n正在生成观测数据图...")
    
    # 统计有数据的观测对象
    total_access_count = len(created_accesses)
    visualized_count = 0
    skipped_count = 0
    
    print(f"总共有 {total_access_count} 个观测对象，正在逐个检查和可视化...")
    
    for i, access in enumerate(created_accesses):
        access_name = f"{access.station_id} → {access.satellite_id} ({access.obs_type})"
        print(f"\n处理观测对象 {i+1}/{total_access_count}: {access_name}")
        
        # 检查是否有观测数据
        if len(access.data) == 0:
            print(f"  ⚠️  跳过：该观测对象没有观测数据")
            skipped_count += 1
            continue
        
        print(f"  ✅ 发现 {len(access.data)} 个观测数据点，正在生成可视化...")
        
        try:
            # 生成观测数据可视化
            fig, axes = visualize.visualize_access(access)
            
            if fig is not None:
                plt.show()
                visualized_count += 1
                
                # 保存图像
                try:
                    filename = f"figs/demo2_access_{access.station_id}_{access.obs_type}.png"
                    fig.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"  📁 观测数据图已保存到 {filename}")
                except Exception as e:
                    print(f"  ❌ 保存图像失败: {e}")
            else:
                print(f"  ❌ 可视化生成失败")
                skipped_count += 1
                
        except Exception as e:
            print(f"  ❌ 生成观测数据可视化时出错: {e}")
            skipped_count += 1
    
    # 显示最终统计结果
    print(f"\n" + "=" * 60)
    print("观测数据可视化完成统计:")
    print(f"  📊 总观测对象数: {total_access_count}")
    print(f"  ✅ 成功可视化: {visualized_count} 个")
    print(f"  ⚠️  跳过/失败: {skipped_count} 个")
    
    # 显示观测摘要
    summary = scenario.get_access_summary()
    print(f"\n观测数据摘要:")
    print(f"  - 总观测对象数: {summary['total_accesses']}")
    print(f"  - 有数据的对象: {summary['with_data']}")
    print(f"  - 按类型分布: {summary['by_type']}")
    
    # 如果有多个有数据的观测对象，生成对比图
    accesses_with_data = scenario.filter_accesses_by_data_count(min_data_count=1)
    if len(accesses_with_data) > 1:
        print(f"\n正在生成多观测对象对比图...")
        try:
            # 选择相同类型的观测对象进行对比（如果有的话）
            azi_ele_with_data = [acc for acc in accesses_with_data if acc.obs_type == 'Azi_Ele']
            if len(azi_ele_with_data) > 1:
                print("生成方位角俯仰角观测对比图...")
                fig_multi, axes_multi = visualize.visualize_multiple_access(
                    azi_ele_with_data,
                    obs_type_filter='Azi_Ele'
                )
                plt.show()
                try:
                    fig_multi.savefig("figs/demo2_multiple_azi_ele_comparison.png", dpi=300, bbox_inches='tight')
                    print("多观测对象对比图已保存到 figs/demo2_multiple_azi_ele_comparison.png")
                except:
                    print("注意：无法保存对比图像到figs目录")
            else:
                print("只有一个方位角俯仰角观测对象，生成通用对比图...")
                fig_multi, axes_multi = visualize.visualize_multiple_access(
                    accesses_with_data[:3],  # 最多选择3个进行对比
                    obs_type_filter=None
                )
                plt.show()
                try:
                    fig_multi.savefig("figs/demo2_multiple_access_comparison.png", dpi=300, bbox_inches='tight')
                    print("多观测对象对比图已保存到 figs/demo2_multiple_access_comparison.png")
                except:
                    print("注意：无法保存对比图像到figs目录")
        except Exception as e:
            print(f"生成对比图时出错: {e}")
    
    print("\nDemo2 完成！")
    return scenario


def demo3_load_and_visualize():
    """
    Demo3：数据读取和可视化演示
    - 创建satelliteScenario，场景与Demo2相同
    - 卫星星历，观测数据全部从已有数据读取，不重新计算
    - 绘制与Demo2一样的图
    """
    print("=" * 80)
    print("Demo3: 数据读取和可视化演示")
    print("=" * 80)
    
    # 检查数据文件是否存在
    data_files_exist = (
        os.path.exists("data/ephemeris_OBS-SAT-001.txt") and
        os.path.exists("data/access_data_BJ-001_OBS-SAT-001_Azi_Ele.txt")
    )
    
    if not data_files_exist:
        print("警告: 未找到必要的数据文件，请先运行Demo2生成数据")
        print("正在运行Demo2以生成数据...")
        demo2_satellite_observation()
        print("数据生成完成，继续Demo3...")
    
    # 设置时间参数（与Demo2相同）
    start_time = datetime.datetime(2023, 10, 1, 0, 0, 0)
    end_time = start_time + datetime.timedelta(hours=6)
    time_step = 60
    
    # 创建场景（与Demo2相同）
    scenario = SatelliteScenario(
        name="Data Loading Demo",
        introduction="Demonstration of loading satellite ephemeris and observation data from files",
        start_time=start_time,
        end_time=end_time,
        time_step=time_step
    )
    
    # 创建相同的地面站
    ground_stations = [
        GroundStation(
            name="Beijing Station",
            station_id="BJ-001",
            longitude=116.3,
            latitude=39.9,
            altitude=44
        ),
        GroundStation(
            name="London Station",
            station_id="LDN-002", 
            longitude=-0.1,
            latitude=51.5,
            altitude=25
        ),
        GroundStation(
            name="Sydney Station",
            station_id="SYD-003",
            longitude=151.2,
            latitude=-33.9,
            altitude=58
        )
    ]
    
    for station in ground_stations:
        scenario.add_ground_station(station)
    
    # 创建相同的卫星（但不计算轨道）
    satellite = Satellite(
        name="Observation Target",
        satellite_id="OBS-SAT-001",
        initial_kepler_elements={
            'a': 7200.0,
            'e': 0.001,
            'i': 45.0,
            'Omega': 100.0,
            'omega': 0.0,
            'M0': 0.0
        }
    )
    
    scenario.add_satellite(satellite)
    
    # 创建相同的观测对象（但不计算数据）
    obs_configs = [
        ("BJ-001", "OBS-SAT-001", "Azi_Ele"),
        ("LDN-002", "OBS-SAT-001", "RA_DEC"),
        ("SYD-003", "OBS-SAT-001", "R_RD")
    ]
    
    for station_id, sat_id, obs_type in obs_configs:
        scenario.create_access(station_id, sat_id, obs_type)
    
    print(f"已创建场景包含:")
    print(f"  - {len(scenario.ground_stations)} 个地面站")
    print(f"  - {len(scenario.satellites)} 颗卫星")
    print(f"  - {len(scenario.accesses)} 个观测对象")
    
    # 从文件读取星历数据
    print("\n正在从文件读取卫星星历数据...")
    scenario.load_all_satellite_ephemeris("data")
    
    # 计算星下点轨迹
    print("正在计算星下点轨迹...")
    scenario.satellites[0].calculate_ground_track()
    
    # 从文件读取观测数据
    print("\n正在从文件读取观测数据...")
    scenario.load_all_access_data("data/access_data")
    
    # 显示读取结果摘要
    summary = scenario.get_access_summary()
    print(f"\n数据读取摘要:")
    print(f"  - 卫星星历数据点: {len(scenario.satellites[0].eph['time'])}")
    print(f"  - 观测对象总数: {summary['total_accesses']}")
    print(f"  - 有数据的观测对象: {summary['with_data']}")
    
    # 生成相同的可视化图形
    print("\n正在生成可视化图形...")
    
    # 3D轨道图
    print("正在生成3D轨道图...")
    fig_orbits, ax_orbits = visualize.visualize_orbits(scenario)
    plt.show()
    try:
        os.makedirs("figs", exist_ok=True)
        fig_orbits.savefig("figs/demo3_satellite_orbits.png", dpi=300, bbox_inches='tight')
        print("3D轨道图已保存到 figs/demo3_satellite_orbits.png")
    except Exception as e:
        print(f"保存3D轨道图失败: {e}")
    
    # 星下点轨迹图
    print("正在生成星下点轨迹图...")
    fig_track, ax_track = visualize.visualize_ground_track(scenario)
    plt.show()
    try:
        fig_track.savefig("figs/demo3_ground_track.png", dpi=300, bbox_inches='tight')
        print("星下点轨迹图已保存到 figs/demo3_ground_track.png")
    except Exception as e:
        print(f"保存星下点轨迹图失败: {e}")
    
    # 地面站分布图
    print("正在生成地面站分布图...")
    fig_stations, ax_stations = visualize.visualize_stations(
        scenario,
        show_altitude=True,
        altitude_colormap='viridis',
        size_by_altitude=True,
        station_size=200
    )
    plt.show()
    try:
        fig_stations.savefig("figs/demo3_ground_stations.png", dpi=300, bbox_inches='tight')
        print("地面站分布图已保存到 figs/demo3_ground_stations.png")
    except Exception as e:
        print(f"保存地面站分布图失败: {e}")
    
    # 观测数据图
    print("正在生成观测数据图...")
    accesses_with_data = scenario.filter_accesses_by_data_count(min_data_count=1)
    
    for i, access in enumerate(accesses_with_data):
        print(f"正在可视化观测数据 {i+1}/{len(accesses_with_data)}: "
              f"{access.station_id} → {access.satellite_id} ({access.obs_type})")
        
        fig, axes = visualize.visualize_access(access)
        plt.show()
        
        try:
            filename = f"figs/demo3_access_{access.station_id}_{access.obs_type}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"观测数据图已保存到 {filename}")
        except Exception as e:
            print(f"保存观测数据图失败: {e}")
    
    print("\nDemo3 完成！")
    print("成功演示了从文件读取数据并生成相同的可视化图形")
    return scenario


def main():
    """主函数：运行所有Demo"""
    print("卫星轨道和观测仿真演示程序")
    print("包含三个独立的Demo：")
    print("Demo1: 卫星轨道演示")
    print("Demo2: 卫星观测演示") 
    print("Demo3: 数据读取和可视化演示")
    print()
    
    while True:
        print("请选择要运行的Demo:")
        print("1 - Demo1: 卫星轨道演示")
        print("2 - Demo2: 卫星观测演示")
        print("3 - Demo3: 数据读取和可视化演示")
        print("4 - 运行所有Demo")
        print("0 - 退出")
        
        choice = input("请输入选择 (0-4): ").strip()
        
        if choice == '1':
            demo1_satellite_orbits()
        elif choice == '2':
            demo2_satellite_observation()
        elif choice == '3':
            demo3_load_and_visualize()
        elif choice == '4':
            demo1_satellite_orbits()
            demo2_satellite_observation()
            demo3_load_and_visualize()
        elif choice == '0':
            print("程序结束，再见！")
            break
        else:
            print("无效的选择，请重新输入")
        
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # 可以直接运行特定的Demo，或运行主菜单
    # demo1_satellite_orbits()    # 取消注释运行Demo1
    # demo2_satellite_observation()  # 取消注释运行Demo2  
    # demo3_load_and_visualize()  # 取消注释运行Demo3
    main()  # 运行交互式菜单