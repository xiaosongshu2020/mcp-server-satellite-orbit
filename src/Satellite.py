import numpy as np
import datetime
from src.orbitTools import kpl2cts
from astropy.coordinates import GCRS, ITRS, CartesianRepresentation
from astropy.time import Time
import astropy.units as u


class Satellite:
    """
    卫星对象类，包含卫星的基本信息和轨道计算功能
    """
    def __init__(self, name, satellite_id, initial_kepler_elements=None,
                  epoch=None, orbitColor=None, showLabel=True, eph=None,
                  showPoint=True, eph_coord="GCRS"):
        """
        初始化卫星对象
        
        参数:
        name (str): 卫星名称
        satellite_id (str): 卫星编号
        initial_kepler_elements (dict): 初始开普勒根数，包含:
            - a: 半长轴 (km)
            - e: 偏心率
            - i: 轨道倾角 (deg)
            - Omega: 升交点赤经 (deg)
            - omega: 近地点幅角 (deg)
            - M0: 平近点角 (deg)
        epoch (datetime): 历元时刻，默认为当前时间
        orbitColor (list): RGB颜色数组，默认为枚举颜色
        showLabel (bool): 是否显示标签
        eph (dict): 星历数据，包含:
            - time: datetime对象数组
            - cartesian: 位置速度数组，每个元素为[x,y,z,vx,vy,vz]
        eph_coord (str): 星历数据所处的坐标系，默认为"GCRS"
        """
        import colorEnumerator
        colorEnum = colorEnumerator.colorEnumerator()

        self.name = name
        self.satellite_id = satellite_id
        self.kepler_elements = initial_kepler_elements
        self.epoch = epoch if epoch else datetime.datetime.now()
        self.orbitColor = orbitColor if orbitColor is not None else colorEnum.next_color()  # 默认为黑色
        self.showLabel = showLabel
        self.showPoint = showPoint  # 是否显示卫星位置点
        self.eph_coord = eph_coord  # 星历数据所处的坐标系
        
        # 惯性系星历数据存储（GCRS坐标系，字典格式）
        if eph is not None:
            # 验证星历数据格式
            if not isinstance(eph, dict) or 'time' not in eph or 'cartesian' not in eph:
                raise ValueError("星历数据必须是包含'time'和'cartesian'键的字典")
            
            # 确保时间数据都是datetime对象
            time_array = []
            for t in eph['time']:
                if isinstance(t, datetime.datetime):
                    time_array.append(t)
                else:
                    raise ValueError("时间数据必须是datetime对象")
            
            self.eph = {
                'time': time_array,
                'cartesian': np.array(eph['cartesian'])  # 转换为numpy数组
            }
        else:
            # 初始化空的惯性系星历数据
            self.eph = {
                'time': [],
                'cartesian': []
            }
        
        # 地固系星历数据存储（ITRF坐标系，字典格式）
        self.eph_itrf = {
            'time': [],
            'cartesian': []
        }
        
        # 星下点数据存储（经纬度数组）
        # 每个元素为[经度, 纬度]，单位为度
        self.ground_track = []

    def propagate_orbit(self, start_time, end_time, time_step):
        """
        使用二体模型生成卫星轨道
        
        参数:
        start_time (datetime): 开始时间
        end_time (datetime): 结束时间
        time_step (float): 时间步长（秒）
        
        返回:
        None (更新类内部的星历数据)
        """
        if self.kepler_elements is None:
            raise ValueError("需要初始开普勒根数来计算轨道")
            
        # 地球引力常数 (km³/s²)
        mu = 398600.4418
        
        # 清空惯性系星历数据
        self.eph = {
            'time': [],
            'cartesian': []
        }
        # 清空地固系星历数据
        self.eph_itrf = {
            'time': [],
            'cartesian': []
        }
        # 清空星下点数据
        self.ground_track = []
        
        # 计算时间范围
        current_time = start_time
        while current_time <= end_time:
            # 计算当前时刻与历元的时间差（秒）
            dt = (current_time - self.epoch).total_seconds()
            
            # 简单的二体模型计算（这里只是框架，实际的轨道计算会更复杂）
            # 计算当前时刻的平近点角
            n = np.sqrt(mu / self.kepler_elements['a']**3) * 180.0 / np.pi  # 平均运动
            M = self.kepler_elements['M0'] + n * dt
            
            kpl = [self.kepler_elements['a'], self.kepler_elements['e'],
                   self.kepler_elements['i'], self.kepler_elements['Omega'],
                   self.kepler_elements['omega'], M]
            
            # 计算开普勒元素到笛卡尔坐标系的转换
            cts = kpl2cts(np.array(kpl))

            # 存储位置、速度和时间数据到星历
            self.eph['time'].append(current_time)
            self.eph['cartesian'].append(cts)  # cts包含[x,y,z,vx,vy,vz]
            
            # 更新时间
            current_time += datetime.timedelta(seconds=time_step)
        
        # 将cartesian转换为numpy数组
        self.eph['cartesian'] = np.array(self.eph['cartesian'])
            
    def get_position_at_time(self, time):
        """
        获取指定时间的卫星位置
        
        参数:
        time (datetime): 查询时间
        
        返回:
        np.array: 卫星位置 [x, y, z]
        """
        if len(self.eph['time']) == 0:
            return np.array([0, 0, 0])  # 没有星历数据时返回默认值
        
        # 简单的最近邻插值
        time_diffs = [abs((t - time).total_seconds()) for t in self.eph['time']]
        min_index = np.argmin(time_diffs)
        
        # 返回位置部分（前3个元素）
        return self.eph['cartesian'][min_index][:3]

    def get_velocity_at_time(self, time):
        """
        获取指定时间的卫星速度
        
        参数:
        time (datetime): 查询时间
        
        返回:
        np.array: 卫星速度 [vx, vy, vz]
        """
        if len(self.eph['time']) == 0:
            return np.array([0, 0, 0])  # 没有星历数据时返回默认值
        
        # 简单的最近邻插值
        time_diffs = [abs((t - time).total_seconds()) for t in self.eph['time']]
        min_index = np.argmin(time_diffs)
        
        # 返回速度部分（后3个元素）
        return self.eph['cartesian'][min_index][3:6]

    def save_ephemeris_data(self, filename):
        """
        保存星历数据到文本文件
        
        文件格式: 固定宽度的空格分隔格式
        MJD_day    MJD_sec    X(km)    Y(km)    Z(km)    VX(km/s)    VY(km/s)    VZ(km/s)
        
        参数:
        filename (str): 输出文件路径
        """
        if len(self.eph['time']) == 0:
            print("警告: 没有星历数据可保存")
            return
        
        try:
            with open(filename, 'w') as f:
                # 写入文件头
                f.write(f"# 卫星星历数据文件\n")
                f.write(f"# 卫星名称: {self.name}\n")
                f.write(f"# 卫星编号: {self.satellite_id}\n")
                f.write(f"# 坐标系: {self.eph_coord}\n")
                f.write(f"# 格式: 固定宽度空格分隔\n")
                f.write(f"# 列说明: MJD_Day    MJD_Sec         X(km)           Y(km)           Z(km)           VX(km/s)        VY(km/s)        VZ(km/s)\n")
                f.write(f"# 数据点数: {len(self.eph['time'])}\n")
                f.write("#\n")  # 分隔行
                
                # 写入数据
                for time_obj, state_vector in zip(self.eph['time'], self.eph['cartesian']):
                    mjd_total = self._datetime_to_mjd(time_obj)
                    mjd_day = int(mjd_total)
                    mjd_sec = (mjd_total - mjd_day) * 86400.0
                    
                    # 使用固定宽度格式化输出
                    f.write(f"{mjd_day:8d} {mjd_sec:12.6f} {state_vector[0]:15.6f} {state_vector[1]:15.6f} "
                           f"{state_vector[2]:15.6f} {state_vector[3]:15.6f} {state_vector[4]:15.6f} {state_vector[5]:15.6f}\n")
            
            print(f"卫星 {self.satellite_id} 星历数据已保存到 {filename}")
            
        except Exception as e:
            print(f"保存星历文件时发生错误: {e}")
    
    def load_ephemeris_data(self, filename):
        """
        从文本文件读取星历数据
        
        文件格式: 固定宽度的空格分隔格式
        MJD_day    MJD_sec    X(km)    Y(km)    Z(km)    VX(km/s)    VY(km/s)    VZ(km/s)
        
        参数:
        filename (str): 星历数据文件路径
        """
        self.eph = {
            'time': [],
            'cartesian': []
        }
        # 清空星下点数据
        self.ground_track = []
        
        try:
            with open(filename, 'r') as f:
                coord_system = "GCRS"  # 默认坐标系
                
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释行，但解析坐标系信息
                    if not line or line.startswith('#'):
                        if line.startswith('# 坐标系:'):
                            coord_system = line.split(':')[1].strip()
                        continue
                    
                    try:
                        # 使用空格分隔数据
                        parts = line.split()
                        if len(parts) < 8:  # 需要8个数据: MJD day, MJD sec, x, y, z, vx, vy, vz
                            print(f"警告: 第{line_num}行数据格式不正确，跳过")
                            continue
                        
                        # 解析MJD时间
                        mjd_day = float(parts[0])
                        mjd_sec = float(parts[1])
                        mjd_total = mjd_day + mjd_sec / 86400.0  # 转换为完整的MJD
                        
                        # 转换MJD到datetime对象
                        time_obj = self._mjd_to_datetime(mjd_total)
                        
                        # 解析状态向量数据
                        state_vector = [float(x) for x in parts[2:8]]  # x, y, z, vx, vy, vz
                        
                        self.eph['time'].append(time_obj)
                        self.eph['cartesian'].append(state_vector)
                        
                    except (ValueError, IndexError) as e:
                        print(f"警告: 第{line_num}行数据解析错误: {e}")
                        continue
            
            # 将cartesian转换为numpy数组
            self.eph['cartesian'] = np.array(self.eph['cartesian'])
            self.eph_coord = coord_system
            
            print(f"成功读取卫星 {self.satellite_id} 的 {len(self.eph['time'])} 条星历数据")
            
        except FileNotFoundError:
            print(f"错误: 找不到文件 {filename}")
        except Exception as e:
            print(f"读取星历文件时发生错误: {e}")

    def _datetime_to_mjd(self, dt):
        """
        将datetime对象转换为修正儒略日(MJD)
        
        参数:
        dt (datetime): datetime对象
        
        返回:
        float: 对应的MJD
        """
        try:
            from astropy.time import Time
            astropy_time = Time(dt.isoformat())
            return astropy_time.mjd
        except:
            # 简化计算方法（备用）
            epoch = datetime.datetime(1858, 11, 17)  # MJD起始时间
            delta = dt - epoch
            return delta.total_seconds() / 86400.0

    def _mjd_to_datetime(self, mjd):
        """
        将修正儒略日(MJD)转换为datetime对象
        
        参数:
        mjd (float): 修正儒略日
        
        返回:
        datetime: 对应的datetime对象
        """
        try:
            from astropy.time import Time
            astropy_time = Time(mjd, format='mjd')
            return astropy_time.to_datetime()
        except:
            # 简化计算方法（备用）
            epoch = datetime.datetime(1858, 11, 17)  # MJD起始时间
            delta = datetime.timedelta(days=mjd)
            return epoch + delta

    def eph_GCRS2ITRF(self):
        """
        将GCRS坐标系下的惯性系星历转换到ITRF坐标系，存储为地固系星历
        
        该方法会将self.eph中的惯性系星历数据转换后存储到self.eph_itrf中
        
        注意:
        - 只有当前坐标系为GCRS时才进行转换
        - 转换后的地固系星历存储在eph_itrf中
        - 原有的惯性系星历保持不变
        - 需要安装astropy库
        
        返回:
        None (将转换结果存储在eph_itrf中)
        """
        if self.eph_coord != "GCRS":
            raise ValueError(f"当前坐标系为{self.eph_coord}，只能从GCRS转换到ITRF")
        
        if len(self.eph['time']) == 0:
            print("警告: 惯性系星历数据为空，无法进行坐标系转换")
            return
        
        # 转换星历数据
        converted_cartesian = []
        
        for i, (time_point, state_vector) in enumerate(zip(self.eph['time'], self.eph['cartesian'])):
            try:
                # 提取位置和速度 (km, km/s)
                position = state_vector[:3]  # [x, y, z]
                velocity = state_vector[3:6]  # [vx, vy, vz]
                
                # 转换datetime到astropy Time对象
                astropy_time = Time(time_point.isoformat())
                
                # 创建GCRS坐标对象（位置）
                gcrs_pos = GCRS(
                    CartesianRepresentation(
                        x=position[0] * u.km,
                        y=position[1] * u.km,
                        z=position[2] * u.km
                    ),
                    obstime=astropy_time
                )
                
                # 创建GCRS坐标对象（速度）
                gcrs_vel = GCRS(
                    CartesianRepresentation(
                        x=velocity[0] * u.km / u.s,
                        y=velocity[1] * u.km / u.s,
                        z=velocity[2] * u.km / u.s
                    ),
                    obstime=astropy_time
                )
                
                # 转换到ITRS坐标系
                itrs_pos = gcrs_pos.transform_to(ITRS(obstime=astropy_time))
                itrs_vel = gcrs_vel.transform_to(ITRS(obstime=astropy_time))
                
                # 提取转换后的坐标值
                converted_position = [
                    itrs_pos.cartesian.x.to(u.km).value,
                    itrs_pos.cartesian.y.to(u.km).value,
                    itrs_pos.cartesian.z.to(u.km).value
                ]
                
                converted_velocity = [
                    itrs_vel.cartesian.x.to(u.km/u.s).value,
                    itrs_vel.cartesian.y.to(u.km/u.s).value,
                    itrs_vel.cartesian.z.to(u.km/u.s).value
                ]
                
                # 组合位置和速度
                converted_state = converted_position + converted_velocity
                converted_cartesian.append(converted_state)
                
            except Exception as e:
                print(f"转换第{i}个时刻的坐标时出错: {e}")
                # 如果转换失败，保持原坐标
                converted_cartesian.append(state_vector)
        
        # 更新地固系星历数据
        self.eph_itrf = {
            'time': self.eph['time'].copy(),  # 复制时间数组
            'cartesian': np.array(converted_cartesian)
        }
        
        print(f"成功将{len(converted_cartesian)}个时刻的星历从GCRS转换到ITRF坐标系")
        print(f"惯性系星历保持在GCRS坐标系，地固系星历存储在ITRF坐标系")

    def get_coordinate_system(self):
        """
        获取当前惯性系星历数据的坐标系
        
        返回:
        str: 坐标系名称
        """
        return self.eph_coord

    def set_coordinate_system(self, coord_system):
        """
        手动设置坐标系标识（注意：这不会进行实际的坐标转换）
        
        参数:
        coord_system (str): 坐标系名称
        """
        self.eph_coord = coord_system
    
    def get_itrf_ephemeris(self):
        """
        获取地固系星历数据
        
        返回:
        dict: 地固系星历数据，包含'time'和'cartesian'键
        """
        return self.eph_itrf
    
    def has_itrf_ephemeris(self):
        """
        检查是否有地固系星历数据
        
        返回:
        bool: 是否有地固系星历数据
        """
        return len(self.eph_itrf['time']) > 0
    
    def ensure_itrf_ephemeris(self):
        """
        确保有地固系星历数据，如果没有则进行转换
        
        返回:
        bool: 是否成功获得地固系星历数据
        """
        if self.has_itrf_ephemeris():
            return True
        
        if len(self.eph['time']) == 0:
            print("警告: 没有惯性系星历数据，无法生成地固系星历")
            return False
        
        if self.eph_coord == "GCRS":
            print("正在从GCRS惯性系星历转换到ITRF地固系星历...")
            self.eph_GCRS2ITRF()
            return self.has_itrf_ephemeris()
        else:
            print(f"警告: 当前惯性系星历坐标系为{self.eph_coord}，无法自动转换到ITRF")
            return False

    def calculate_ground_track(self):
        """
        计算卫星的星下点轨迹
        
        该方法使用地固系星历（ITRF坐标系）计算星下点轨迹。
        如果没有地固系星历，会自动从惯性系星历转换。
        
        返回:
        list: 星下点轨迹，每个元素为[经度, 纬度]，单位为度
              经度范围: [-180, 180]
              纬度范围: [-90, 90]
        """
        # 确保有地固系星历数据
        if not self.ensure_itrf_ephemeris():
            print("错误: 无法获得地固系星历数据，无法计算星下点")
            self.ground_track = []
            return self.ground_track
        
        # 清空之前的星下点数据
        self.ground_track = []
        
        # 使用地固系星历计算每个时刻的星下点
        for i, (time_point, state_vector) in enumerate(zip(self.eph_itrf['time'], self.eph_itrf['cartesian'])):
            try:
                # 提取ITRF坐标系下的位置 (km)
                position = state_vector[:3]  # [x, y, z]
                
                # 方法1: 使用astropy进行精确转换
                try:
                    # 转换datetime到astropy Time对象
                    astropy_time = Time(time_point.isoformat())
                    
                    # 创建ITRS坐标对象
                    itrs_coord = ITRS(
                        CartesianRepresentation(
                            x=position[0] * u.km,
                            y=position[1] * u.km,
                            z=position[2] * u.km
                        ),
                        obstime=astropy_time
                    )
                    
                    # 转换为地理坐标
                    geo_coord = itrs_coord.earth_location
                    longitude = geo_coord.lon.deg  # 经度（度）
                    latitude = geo_coord.lat.deg   # 纬度（度）
                    
                except Exception as astropy_error:
                    print(f"Astropy转换失败，使用简化方法: {astropy_error}")
                    # 方法2: 使用简化的球面坐标转换（备用方法）
                    longitude, latitude = self._cartesian_to_lonlat_simple(position)
                
                # 确保经度在[-180, 180]范围内
                while longitude > 180:
                    longitude -= 360
                while longitude < -180:
                    longitude += 360
                
                # 添加到星下点轨迹
                self.ground_track.append([longitude, latitude])
                
            except Exception as e:
                print(f"计算第{i}个时刻的星下点时出错: {e}")
                # 如果计算失败，添加默认值
                self.ground_track.append([0.0, 0.0])
        
        print(f"成功计算{len(self.ground_track)}个时刻的星下点")
        return self.ground_track

    def _cartesian_to_lonlat_simple(self, position):
        """
        简化的笛卡尔坐标到经纬度转换（备用方法）
        
        参数:
        position (array): ITRF坐标系下的位置 [x, y, z] (km)
        
        返回:
        tuple: (经度, 纬度) 单位为度
        """
        x, y, z = position
        
        # 计算经度
        longitude = np.arctan2(y, x) * 180.0 / np.pi
        
        # 计算纬度
        r = np.sqrt(x**2 + y**2 + z**2)
        latitude = np.arcsin(z / r) * 180.0 / np.pi
        
        return longitude, latitude

    def get_ground_track(self):
        """
        获取星下点轨迹
        
        返回:
        list: 星下点轨迹，每个元素为[经度, 纬度]，单位为度
        """
        if len(self.ground_track) == 0:
            # 如果没有计算过星下点轨迹，尝试计算
            self.calculate_ground_track()

        return self.ground_track

    def get_ground_point_at_time(self, time):
        """
        获取指定时间的星下点位置
        
        参数:
        time (datetime): 查询时间
        
        返回:
        list: [经度, 纬度]，单位为度；如果没有数据返回[0, 0]
        """
        if len(self.ground_track) == 0 or len(self.eph['time']) == 0:
            return [0.0, 0.0]
        
        # 简单的最近邻插值
        time_diffs = [abs((t - time).total_seconds()) for t in self.eph['time']]
        min_index = np.argmin(time_diffs)
        
        return self.ground_track[min_index]