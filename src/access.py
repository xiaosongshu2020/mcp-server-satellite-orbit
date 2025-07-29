import numpy as np
import datetime
from astropy.time import Time
from astropy.coordinates import ITRS, EarthLocation, AltAz, GCRS, CartesianRepresentation
from astropy import units as u
import astropy.coordinates as coord


class Access:
    """
    地面站对卫星的观测对象类
    
    用于模拟和处理地面站对卫星的观测活动，包括方位角俯仰角、
    赤经赤纬、测距测速等不同类型的观测数据。
    """
    
    def __init__(self, station_id, satellite_id, obs_type='Azi_Ele'):
        """
        初始化观测对象
        
        参数:
        station_id (str): 观测站编号
        satellite_id (str): 卫星编号
        obs_type (str): 观测数据类型
                       'Azi_Ele': 方位角俯仰角 [azimuth(deg), elevation(deg)]
                       'RA_DEC': 赤经赤纬 [ra(deg), dec(deg)]
                       'R_RD': 测距测速 [range(km), range_rate(km/s)]
        """
        self.station_id = station_id
        self.satellite_id = satellite_id
        self.obs_type = obs_type
        
        # 观测数据存储
        self.times = []  # datetime对象列表
        self.data = []   # 观测数据列表，每个元素根据obs_type包含不同数量的数值
        
        # 验证观测类型
        valid_types = ['Azi_Ele', 'RA_DEC', 'R_RD']
        if obs_type not in valid_types:
            raise ValueError(f"不支持的观测类型: {obs_type}，支持的类型: {valid_types}")
    
    def read_observation_data(self, filename):
        """
        从文本文件读取观测数据
        
        文件格式: 固定宽度的空格分隔格式
        MJD_day    MJD_sec         数据1        数据2        ...
        
        参数:
        filename (str): 观测数据文件路径
        """
        self.times = []
        self.data = []
        
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释行
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        # 使用空格分隔数据
                        parts = line.split()
                        if len(parts) < 3:  # 至少需要MJD day, MJD sec, 一个数据
                            print(f"警告: 第{line_num}行数据格式不正确，跳过")
                            continue
                        
                        # 解析MJD时间
                        mjd_day = float(parts[0])
                        mjd_sec = float(parts[1])
                        mjd_total = mjd_day + mjd_sec / 86400.0  # 转换为完整的MJD
                        
                        # 转换MJD到datetime对象
                        time_obj = self._mjd_to_datetime(mjd_total)
                        
                        # 解析观测数据
                        obs_data = [float(x) for x in parts[2:]]
                        
                        # 验证数据长度
                        expected_length = self._get_expected_data_length()
                        if len(obs_data) != expected_length:
                            print(f"警告: 第{line_num}行数据长度不匹配，期望{expected_length}个数据，实际{len(obs_data)}个")
                            continue
                        
                        self.times.append(time_obj)
                        self.data.append(obs_data)
                        
                    except (ValueError, IndexError) as e:
                        print(f"警告: 第{line_num}行数据解析错误: {e}")
                        continue
            
            print(f"成功读取{len(self.times)}条观测数据")
            
        except FileNotFoundError:
            print(f"错误: 找不到文件 {filename}")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
    
    def save_observation_data(self, filename):
        """
        保存观测数据到文本文件
        
        文件格式: 固定宽度的空格分隔格式
        MJD_day    MJD_sec         数据1        数据2        ...
        
        参数:
        filename (str): 输出文件路径
        """
        if len(self.times) == 0:
            print("警告: 没有观测数据可保存")
            return
        
        try:
            with open(filename, 'w') as f:
                # 写入文件头
                f.write(f"# 观测数据文件\n")
                f.write(f"# 观测站编号: {self.station_id}\n")
                f.write(f"# 卫星编号: {self.satellite_id}\n")
                f.write(f"# 观测类型: {self.obs_type}\n")
                f.write(f"# 格式: 固定宽度空格分隔\n")
                f.write(f"# 列说明: MJD_Day    MJD_Sec         ")
                
                if self.obs_type == 'Azi_Ele':
                    f.write("Azimuth(deg)    Elevation(deg)\n")
                    header = f"# {'MJD_Day':>8} {'MJD_Sec':>12} {'Azimuth':>12} {'Elevation':>12}\n"
                elif self.obs_type == 'RA_DEC':
                    f.write("RA(deg)         DEC(deg)\n")
                    header = f"# {'MJD_Day':>8} {'MJD_Sec':>12} {'RA':>12} {'DEC':>12}\n"
                elif self.obs_type == 'R_RD':
                    f.write("Range(km)       Range_Rate(km/s)\n")
                    header = f"# {'MJD_Day':>8} {'MJD_Sec':>12} {'Range':>12} {'Range_Rate':>12}\n"
                
                f.write(header)
                f.write(f"# 数据点数: {len(self.times)}\n")
                f.write("#\n")  # 分隔行
                
                # 写入数据
                for time_obj, obs_data in zip(self.times, self.data):
                    mjd_total = self._datetime_to_mjd(time_obj)
                    mjd_day = int(mjd_total)
                    mjd_sec = (mjd_total - mjd_day) * 86400.0
                    
                    # 使用固定宽度格式化输出
                    if len(obs_data) == 2:
                        f.write(f"{mjd_day:8d} {mjd_sec:12.6f} {obs_data[0]:12.6f} {obs_data[1]:12.6f}\n")
                    else:
                        # 处理其他数据长度
                        data_str = ' '.join([f"{x:12.6f}" for x in obs_data])
                        f.write(f"{mjd_day:8d} {mjd_sec:12.6f} {data_str}\n")
            
            print(f"观测数据已保存到 {filename}")
            
        except Exception as e:
            print(f"保存文件时发生错误: {e}")
    
    def calculate_observation_data(self, scenario, start_time=None, end_time=None, 
                                 time_step=None, elevation_mask=10.0):
        """
        计算观测数据
        
        参数:
        scenario (SatelliteScenario): 卫星场景对象
        start_time (datetime): 开始时间，默认使用场景时间
        end_time (datetime): 结束时间，默认使用场景时间
        time_step (float): 时间步长（秒），默认使用场景步长
        elevation_mask (float): 最小仰角限制（度），默认10度
        """
        # 使用场景的时间参数
        start_time = start_time or scenario.start_time
        end_time = end_time or scenario.end_time
        time_step = time_step or scenario.time_step
        
        # 查找对应的卫星和地面站
        satellite = None
        ground_station = None
        
        for sat in scenario.satellites:
            if sat.satellite_id == self.satellite_id:
                satellite = sat
                break
        
        for station in scenario.ground_stations:
            if station.station_id == self.station_id:
                ground_station = station
                break
        
        if satellite is None:
            raise ValueError(f"找不到卫星编号: {self.satellite_id}")
        if ground_station is None:
            raise ValueError(f"找不到地面站编号: {self.station_id}")
        
        # 确保卫星有惯性系星历数据
        if len(satellite.eph['time']) == 0:
            print(f"卫星 {self.satellite_id} 没有惯性系星历数据，正在计算轨道...")
            satellite.propagate_orbit(start_time, end_time, time_step)
        
        # 确保卫星有地固系星历数据用于观测计算
        if not satellite.ensure_itrf_ephemeris():
            print(f"错误: 卫星 {self.satellite_id} 无法获得地固系星历数据")
            return
        
        # 创建地面站的EarthLocation对象
        station_location = EarthLocation(
            lon=ground_station.longitude * u.deg,
            lat=ground_station.latitude * u.deg,
            height=ground_station.altitude * u.m
        )
        
        # 清空现有数据
        self.times = []
        self.data = []
        
        # 使用地固系星历计算每个时刻的观测数据
        for time_point, state_vector in zip(satellite.eph_itrf['time'], satellite.eph_itrf['cartesian']):
            try:
                # 转换时间到astropy Time对象
                astropy_time = Time(time_point.isoformat())
                
                # 获取卫星在ITRF坐标系下的位置和速度
                sat_position = state_vector[:3] * u.km  # [x, y, z]
                sat_velocity = state_vector[3:6] * u.km / u.s  # [vx, vy, vz]
                
                # 创建卫星的ITRS坐标对象
                sat_itrs = ITRS(
                    CartesianRepresentation(
                        x=sat_position[0],
                        y=sat_position[1],
                        z=sat_position[2]
                    ),
                    obstime=astropy_time
                )

                
                # 转换到地面站的地平坐标系
                sat_altaz = sat_itrs.transform_to(
                    AltAz(obstime=astropy_time, location=station_location)
                )
                
                # 检查可见性（仰角限制）
                elevation = sat_altaz.alt.deg
                if elevation < elevation_mask:
                    continue  # 跳过仰角过低的观测
                
                # 根据观测类型计算相应数据
                if self.obs_type == 'Azi_Ele':
                    azimuth = sat_altaz.az.deg
                    obs_data = [azimuth, elevation]
                    
                elif self.obs_type == 'RA_DEC':
                    # 转换到GCRS坐标系以获取赤经赤纬
                    sat_gcrs = sat_itrs.transform_to(GCRS(obstime=astropy_time))
                    ra = sat_gcrs.ra.deg
                    dec = sat_gcrs.dec.deg
                    obs_data = [ra, dec]
                    
                elif self.obs_type == 'R_RD':
                    # 计算测距和测速
                    # 地面站在ITRF坐标系下的位置
                    station_itrs = station_location.get_itrs(obstime=astropy_time)
                    station_pos = np.array([
                        station_itrs.x.to(u.km).value,
                        station_itrs.y.to(u.km).value,
                        station_itrs.z.to(u.km).value
                    ])
                    
                    # 计算相对位置和速度
                    relative_pos = state_vector[:3] - station_pos
                    relative_vel = state_vector[3:6]  # 假设地面站速度为0（简化）
                    
                    # 距离
                    range_km = np.linalg.norm(relative_pos)
                    
                    # 距离变化率（径向速度）
                    range_rate = np.dot(relative_pos, relative_vel) / range_km
                    
                    obs_data = [range_km, range_rate]
                
                else:
                    raise ValueError(f"不支持的观测类型: {self.obs_type}")
                
                # 存储观测数据
                self.times.append(time_point)
                self.data.append(obs_data)
                
            except Exception as e:
                print(f"计算时刻 {time_point} 的观测数据时出错: {e}")
                continue
        
        print(f"成功计算{len(self.times)}个时刻的{self.obs_type}观测数据")
        if len(self.times) > 0:
            print(f"观测时间范围: {self.times[0]} 到 {self.times[-1]}")
    
    def _get_expected_data_length(self):
        """
        根据观测类型返回期望的数据长度
        """
        if self.obs_type == 'Azi_Ele':
            return 2  # 方位角、俯仰角
        elif self.obs_type == 'RA_DEC':
            return 2  # 赤经、赤纬
        elif self.obs_type == 'R_RD':
            return 2  # 测距、测速
        else:
            return 2  # 默认
    
    def _mjd_to_datetime(self, mjd):
        """
        将修正儒略日(MJD)转换为datetime对象
        
        参数:
        mjd (float): 修正儒略日
        
        返回:
        datetime: 对应的datetime对象
        """
        # MJD = JD - 2400000.5
        # 使用astropy的Time对象进行精确转换
        astropy_time = Time(mjd, format='mjd')
        return astropy_time.to_datetime()
    
    def _datetime_to_mjd(self, dt):
        """
        将datetime对象转换为修正儒略日(MJD)
        
        参数:
        dt (datetime): datetime对象
        
        返回:
        float: 对应的MJD
        """
        astropy_time = Time(dt.isoformat())
        return astropy_time.mjd
    
    def get_observation_summary(self):
        """
        获取观测数据摘要信息
        
        返回:
        dict: 观测摘要
        """
        if len(self.data) == 0:
            return {
                'station_id': self.station_id,
                'satellite_id': self.satellite_id,
                'obs_type': self.obs_type,
                'data_count': 0,
                'time_range': None,
                'data_range': None
            }
        
        data_array = np.array(self.data)
        
        summary = {
            'station_id': self.station_id,
            'satellite_id': self.satellite_id,
            'obs_type': self.obs_type,
            'data_count': len(self.data),
            'time_range': (self.times[0], self.times[-1]),
            'data_range': {
                'min': data_array.min(axis=0).tolist(),
                'max': data_array.max(axis=0).tolist(),
                'mean': data_array.mean(axis=0).tolist()
            }
        }
        
        return summary
    
    def filter_by_elevation(self, min_elevation):
        """
        根据仰角过滤观测数据（仅适用于Azi_Ele类型）
        
        参数:
        min_elevation (float): 最小仰角限制（度）
        """
        if self.obs_type != 'Azi_Ele':
            print("警告: 仰角过滤只适用于Azi_Ele观测类型")
            return
        
        if len(self.data) == 0:
            return
        
        filtered_times = []
        filtered_data = []
        
        for time_obj, obs_data in zip(self.times, self.data):
            elevation = obs_data[1]  # 俯仰角是第二个数据
            if elevation >= min_elevation:
                filtered_times.append(time_obj)
                filtered_data.append(obs_data)
        
        removed_count = len(self.times) - len(filtered_times)
        self.times = filtered_times
        self.data = filtered_data
        
        print(f"仰角过滤完成: 移除{removed_count}个低仰角观测点，剩余{len(self.data)}个观测点")


# 使用示例和测试函数
def create_access_example(scenario):
    """
    创建观测对象的示例函数
    
    参数:
    scenario (SatelliteScenario): 卫星场景对象
    
    返回:
    list: Access对象列表
    """
    access_list = []
    
    # 为每个地面站和卫星组合创建不同类型的观测
    obs_types = ['Azi_Ele', 'RA_DEC', 'R_RD']
    
    for station in scenario.ground_stations:
        for satellite in scenario.satellites:
            for obs_type in obs_types:
                access_obj = Access(
                    station_id=station.station_id,
                    satellite_id=satellite.satellite_id,
                    obs_type=obs_type
                )
                access_list.append(access_obj)
    
    return access_list


if __name__ == "__main__":
    # 这里可以添加测试代码
    print("Access模块已加载")