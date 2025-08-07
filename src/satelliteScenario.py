import numpy as np
import datetime

from Earth import Earth
from src.Satellite import Satellite
from src.Station import GroundStation
from src.access import Access
from src.colorEnumerator import colorEnumerator

class SatelliteScenario:
    """
    卫星场景类，包含卫星、地面站和观测对象
    """
    def __init__(self, name="Default Scenario", introduction="", 
                 start_time=None, end_time=None, time_step=None):
        """
        初始化卫星场景对象
        
        参数:
        name (str): 场景名称
        introduction (str): 场景介绍
        start_time (datetime): 开始时间，必须提供
        end_time (datetime): 结束时间，必须提供
        time_step (float): 时间步长（秒），必须提供
        """
        # 验证必需的时间参数
        if start_time is None or end_time is None or time_step is None:
            raise ValueError("必须提供start_time、end_time和time_step参数")
        
        # 验证时间参数类型
        if not isinstance(start_time, datetime.datetime):
            raise ValueError("start_time必须是datetime对象")
        if not isinstance(end_time, datetime.datetime):
            raise ValueError("end_time必须是datetime对象")
        if not isinstance(time_step, (int, float)) or time_step <= 0:
            raise ValueError("time_step必须是正数")
        
        self.name = name  # 场景名称
        self.introduction = introduction  # 场景介绍
        self.satellites = []  # 存储卫星对象列表
        self.ground_stations = []  # 存储地面站对象列表
        self.accesses = []  # 存储观测对象列表
        
        # 时间属性（使用datetime类型）
        self.start_time = start_time
        self.end_time = end_time
        self.time_step = time_step
        
        # 生成时间数组
        self.time = self._generate_time_array()
        
        # 初始化地球对象
        self.earth = Earth()
        
        # 初始化颜色枚举器，用于为卫星分配不同颜色
        self.colorEnum = colorEnumerator()
        
    def _generate_time_array(self):
        """
        根据start_time, end_time, time_step生成时间数组
        
        返回:
        list: datetime对象列表
        """
        time_array = []
        current_time = self.start_time
        while current_time <= self.end_time:
            time_array.append(current_time)
            current_time += datetime.timedelta(seconds=self.time_step)
        return time_array
    
    def add_satellite(self, satellite):
        """
        添加卫星到场景中，并自动分配颜色
        
        参数:
        satellite (Satellite): 卫星对象
        """
        # 自动分配颜色
        satellite.orbitColor = self.colorEnum.next_color()
        self.satellites.append(satellite)
        
    def add_ground_station(self, ground_station):
        """
        添加地面站到场景中
        
        参数:
        ground_station (GroundStation): 地面站对象
        """
        self.ground_stations.append(ground_station)
    
    def add_access(self, access):
        """
        添加观测对象到场景中
        
        参数:
        access (Access): 观测对象
        """
        # 验证观测对象中的地面站和卫星是否存在于场景中
        station_exists = any(station.station_id == access.station_id 
                           for station in self.ground_stations)
        satellite_exists = any(satellite.satellite_id == access.satellite_id 
                             for satellite in self.satellites)
        
        if not station_exists:
            print(f"警告: 地面站 {access.station_id} 不存在于当前场景中")
        
        if not satellite_exists:
            print(f"警告: 卫星 {access.satellite_id} 不存在于当前场景中")
        
        self.accesses.append(access)
        print(f"已添加观测对象: {access.station_id} → {access.satellite_id} ({access.obs_type})")
    
    def create_access(self, station_id, satellite_id, obs_type='Azi_Ele'):
        """
        创建并添加观测对象到场景中（便捷方法）
        
        参数:
        station_id (str): 观测站编号
        satellite_id (str): 卫星编号
        obs_type (str): 观测数据类型
        
        返回:
        Access: 创建的观测对象
        """
        access = Access(station_id, satellite_id, obs_type)
        self.add_access(access)
        return access
    
    def create_all_accesses(self, obs_types=['Azi_Ele'], elevation_mask=10.0):
        """
        为场景中的所有地面站和卫星组合创建观测对象
        
        参数:
        obs_types (list): 观测数据类型列表，默认为['Azi_Ele']
        elevation_mask (float): 最小仰角限制（度），默认10度
        
        返回:
        list: 创建的观测对象列表
        """
        created_accesses = []
        
        for station in self.ground_stations:
            for satellite in self.satellites:
                for obs_type in obs_types:
                    access = Access(
                        station_id=station.station_id,
                        satellite_id=satellite.satellite_id,
                        obs_type=obs_type
                    )
                    self.add_access(access)
                    created_accesses.append(access)
        
        print(f"已创建 {len(created_accesses)} 个观测对象")
        return created_accesses
    
    def calculate_all_accesses(self, start_time=None, end_time=None, 
                             time_step=None, elevation_mask=10.0):
        """
        计算场景中所有观测对象的观测数据
        
        参数:
        start_time (datetime): 开始时间，如果为None则使用场景的start_time
        end_time (datetime): 结束时间，如果为None则使用场景的end_time
        time_step (float): 时间步长（秒），如果为None则使用场景的time_step
        elevation_mask (float): 最小仰角限制（度），默认10度
        """
        if len(self.accesses) == 0:
            print("警告: 场景中没有观测对象，无法计算观测数据")
            return
        
        # 使用传入的参数或场景的默认参数
        calc_start_time = start_time if start_time is not None else self.start_time
        calc_end_time = end_time if end_time is not None else self.end_time
        calc_time_step = time_step if time_step is not None else self.time_step
        
        print(f"开始计算 {len(self.accesses)} 个观测对象的观测数据...")
        
        successful_calculations = 0
        failed_calculations = 0
        
        for i, access in enumerate(self.accesses):
            try:
                print(f"正在计算观测对象 {i+1}/{len(self.accesses)}: "
                      f"{access.station_id} → {access.satellite_id} ({access.obs_type})")
                
                access.calculate_observation_data(
                    scenario=self,
                    start_time=calc_start_time,
                    end_time=calc_end_time,
                    time_step=calc_time_step,
                    elevation_mask=elevation_mask
                )
                
                if len(access.data) > 0:
                    successful_calculations += 1
                    print(f"  成功计算 {len(access.data)} 个观测数据点")
                else:
                    print(f"  未找到满足条件的观测数据（仰角 > {elevation_mask}°）")
                
            except Exception as e:
                failed_calculations += 1
                print(f"  计算失败: {e}")
        
        print(f"\n观测数据计算完成:")
        print(f"  成功: {successful_calculations} 个观测对象")
        print(f"  失败: {failed_calculations} 个观测对象")
        print(f"  总计: {len(self.accesses)} 个观测对象")
    
    def get_accesses_by_station(self, station_id):
        """
        获取指定地面站的所有观测对象
        
        参数:
        station_id (str): 地面站编号
        
        返回:
        list: 观测对象列表
        """
        return [access for access in self.accesses if access.station_id == station_id]
    
    def get_accesses_by_satellite(self, satellite_id):
        """
        获取指定卫星的所有观测对象
        
        参数:
        satellite_id (str): 卫星编号
        
        返回:
        list: 观测对象列表
        """
        return [access for access in self.accesses if access.satellite_id == satellite_id]
    
    def get_accesses_by_type(self, obs_type):
        """
        获取指定类型的所有观测对象
        
        参数:
        obs_type (str): 观测数据类型
        
        返回:
        list: 观测对象列表
        """
        return [access for access in self.accesses if access.obs_type == obs_type]
    
    def filter_accesses_by_data_count(self, min_data_count=1):
        """
        根据观测数据点数量过滤观测对象
        
        参数:
        min_data_count (int): 最小数据点数量
        
        返回:
        list: 符合条件的观测对象列表
        """
        return [access for access in self.accesses if len(access.data) >= min_data_count]
    
    def get_access_summary(self):
        """
        获取场景中所有观测对象的摘要信息
        
        返回:
        dict: 观测摘要信息
        """
        if len(self.accesses) == 0:
            return {
                'total_accesses': 0,
                'by_type': {},
                'by_station': {},
                'by_satellite': {},
                'with_data': 0,
                'without_data': 0
            }
        
        # 按类型统计
        by_type = {}
        for access in self.accesses:
            if access.obs_type not in by_type:
                by_type[access.obs_type] = 0
            by_type[access.obs_type] += 1
        
        # 按地面站统计
        by_station = {}
        for access in self.accesses:
            if access.station_id not in by_station:
                by_station[access.station_id] = 0
            by_station[access.station_id] += 1
        
        # 按卫星统计
        by_satellite = {}
        for access in self.accesses:
            if access.satellite_id not in by_satellite:
                by_satellite[access.satellite_id] = 0
            by_satellite[access.satellite_id] += 1
        
        # 统计有数据和无数据的观测对象
        with_data = sum(1 for access in self.accesses if len(access.data) > 0)
        without_data = len(self.accesses) - with_data
        
        return {
            'total_accesses': len(self.accesses),
            'by_type': by_type,
            'by_station': by_station,
            'by_satellite': by_satellite,
            'with_data': with_data,
            'without_data': without_data
        }
    
    def save_all_access_data(self, base_filename="access_data"):
        """
        保存所有观测对象的数据到文件
        
        参数:
        base_filename (str): 基础文件名，实际文件名会包含观测对象的标识信息
        """
        if len(self.accesses) == 0:
            print("警告: 没有观测对象可保存")
            return
        
        saved_count = 0
        for access in self.accesses:
            if len(access.data) > 0:
                filename = f"{base_filename}_{access.station_id}_{access.satellite_id}_{access.obs_type}.txt"
                try:
                    access.save_observation_data(filename)
                    saved_count += 1
                except Exception as e:
                    print(f"保存观测数据失败 {filename}: {e}")
        
        print(f"已保存 {saved_count} 个观测数据文件")
    
    def save_all_satellite_ephemeris(self, data_dir="data"):
        """
        保存所有卫星的星历数据到文件
        
        参数:
        data_dir (str): 数据目录，默认为"data"
        """
        import os
        
        # 确保目录存在
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"创建目录: {data_dir}")
        
        if len(self.satellites) == 0:
            print("警告: 没有卫星可保存星历数据")
            return
        
        saved_count = 0
        for satellite in self.satellites:
            if len(satellite.eph['time']) > 0:
                filename = os.path.join(data_dir, f"ephemeris_{satellite.satellite_id}.txt")
                try:
                    satellite.save_ephemeris_data(filename)
                    saved_count += 1
                except Exception as e:
                    print(f"保存星历数据失败 {filename}: {e}")
        
        print(f"已保存 {saved_count} 个卫星星历文件到 {data_dir} 目录")
    
    def load_all_satellite_ephemeris(self, data_dir="data"):
        """
        读取所有卫星的星历数据
        
        参数:
        data_dir (str): 数据目录，默认为"data"
        """
        import os
        
        if len(self.satellites) == 0:
            print("警告: 场景中没有卫星，无法读取星历数据")
            return
        
        loaded_count = 0
        for satellite in self.satellites:
            filename = os.path.join(data_dir, f"ephemeris_{satellite.satellite_id}.txt")
            if os.path.exists(filename):
                try:
                    satellite.load_ephemeris_data(filename)
                    loaded_count += 1
                    print(f"成功读取卫星 {satellite.satellite_id} 的惯性系星历数据")
                    
                    # 自动生成地固系星历
                    if satellite.get_coordinate_system() == "GCRS":
                        print(f"正在为卫星 {satellite.satellite_id} 生成地固系星历...")
                        satellite.eph_GCRS2ITRF()
                        
                except Exception as e:
                    print(f"读取星历数据失败 {filename}: {e}")
            else:
                print(f"警告: 找不到卫星 {satellite.satellite_id} 的星历文件: {filename}")
        
        print(f"成功读取 {loaded_count} 个卫星的星历数据")
    
    def load_all_access_data(self, base_filename="access_data"):
        """
        读取所有观测对象的数据
        
        参数:
        base_filename (str): 基础文件名
        """
        if len(self.accesses) == 0:
            print("警告: 场景中没有观测对象，无法读取观测数据")
            return
        
        loaded_count = 0
        for access in self.accesses:
            filename = f"{base_filename}_{access.station_id}_{access.satellite_id}_{access.obs_type}.txt"
            try:
                access.read_observation_data(filename)
                if len(access.data) > 0:
                    loaded_count += 1
                    print(f"成功读取观测数据: {access.station_id} → {access.satellite_id} ({access.obs_type})")
            except Exception as e:
                print(f"读取观测数据失败 {filename}: {e}")
        
        print(f"成功读取 {loaded_count} 个观测对象的数据")
        
    def propagate_all_orbits(self, start_time=None, end_time=None, time_step=None):
        """
        计算所有卫星的轨道
        
        参数:
        start_time (datetime): 开始时间，如果为None则使用初始化时设置的start_time
        end_time (datetime): 结束时间，如果为None则使用初始化时设置的end_time
        time_step (float): 时间步长（秒），如果为None则使用初始化时设置的time_step
        """
        # 使用传入的参数或已设置的属性
        start_time = start_time if start_time is not None else self.start_time
        end_time = end_time if end_time is not None else self.end_time
        time_step = time_step if time_step is not None else self.time_step
        
        # 确保时间参数是datetime类型
        if not isinstance(start_time, datetime.datetime):
            raise ValueError("开始时间必须是datetime对象")
        if not isinstance(end_time, datetime.datetime):
            raise ValueError("结束时间必须是datetime对象")
        
        # 如果传入了新的时间参数，更新场景对象的时间属性和时间数组
        if (start_time != self.start_time or end_time != self.end_time or 
            time_step != self.time_step):
            self.start_time = start_time
            self.end_time = end_time
            self.time_step = time_step
            self.time = self._generate_time_array()
        
        # 计算所有卫星的轨道
        print(f"正在计算 {len(self.satellites)} 颗卫星的轨道...")
        for i, satellite in enumerate(self.satellites):
            print(f"  计算卫星 {i+1}/{len(self.satellites)}: {satellite.name}")
            satellite.propagate_orbit(start_time, end_time, time_step)
            
            # 自动生成地固系星历
            if satellite.get_coordinate_system() == "GCRS":
                print(f"  正在为卫星 {satellite.name} 生成地固系星历...")
                satellite.eph_GCRS2ITRF()
        
        print("所有卫星轨道计算完成！")