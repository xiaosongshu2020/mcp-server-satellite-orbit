import numpy as np


class GroundStation:
    """
    地面站对象类，包含地面站的基本信息
    """
    def __init__(self, name, station_id, longitude, latitude, altitude=0):
        """
        初始化地面站对象
        
        参数:
        name (str): 地面站名称
        station_id (str): 地面站编号
        longitude (float): 经度（度）
        latitude (float): 纬度（度）
        altitude (float): 海拔高度（米）
        """
        self.name = name
        self.station_id = station_id
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        
    def get_ECEF_coordinates(self):
        """
        获取地面站的地心固连坐标系（ECEF）坐标
        
        返回:
        np.array: 地面站的ECEF坐标 [x, y, z]
        """
        # 地球半径（km）
        R_earth = 6378.137
        
        # 将经纬度转换为弧度
        lon_rad = np.radians(self.longitude)
        lat_rad = np.radians(self.latitude)
        
        # 计算ECEF坐标
        x = (R_earth + self.altitude/1000) * np.cos(lat_rad) * np.cos(lon_rad)
        y = (R_earth + self.altitude/1000) * np.cos(lat_rad) * np.sin(lon_rad)
        z = (R_earth + self.altitude/1000) * np.sin(lat_rad)
        
        return np.array([x, y, z])
    
    def check_visibility(self, satellite_position, elevation_mask=10):
        """
        检查卫星是否对地面站可见
        
        参数:
        satellite_position (np.array): 卫星在ECEF坐标系中的位置 [x, y, z]
        elevation_mask (float): 最小仰角（度）
        
        返回:
        bool: 是否可见
        """
        # 需要实现可见性检查逻辑
        return False  # 框架中返回默认值