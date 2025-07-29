import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime

# Cartopy imports for ground track visualization
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def visualize_orbits(scenario, time=None):
    """
    绘制卫星轨道可视化图像 - 修复版本，解决地球遮挡轨道的问题
    
    参数:
    scenario (SatelliteScenario): 卫星场景对象
    time (datetime): 可视化的时间点，默认为None表示使用整个轨道历史
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    # 图形中的字体全部使用"Arial"
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = 'Arial'

    # 创建3D图形
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 关键修复1：禁用自动z-order计算，使用手动控制
    try:
        ax.computed_zorder = False
    except AttributeError:
        pass
    
    # 关键修复2：先绘制卫星轨道（在地球之前），并设置高zorder
    satellite_positions = []  # 存储卫星位置用于后续绘制
    
    for satellite in scenario.satellites:
        # 获取卫星轨道颜色
        orbit_color = satellite.orbitColor
        # 将RGB数组(0-255)转换为matplotlib可接受的格式(0-1)
        if all(0 <= c <= 1 for c in orbit_color):
            color_rgb = orbit_color
        else:
            color_rgb = [c/255 for c in orbit_color]
        
        # 绘制整个轨道 - 设置高zorder确保在地球前面
        if len(satellite.eph['cartesian']) > 0:
            positions = satellite.eph['cartesian'][:, :3]  # 取位置部分
            if satellite.showLabel:
                ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
                        color=color_rgb, linewidth=2, label=satellite.name, zorder=10)
            else:
                ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
                        color=color_rgb, linewidth=2, zorder=10)
            
        # 存储当前时间的卫星位置，稍后绘制
        if time is None:
            time = scenario.start_time  # 如果没有指定时间，使用开始时间
        
        position = satellite.get_position_at_time(time)
        satellite_positions.append((position, color_rgb, satellite.showPoint))

    # 修复3：绘制地球，使用修改后的绘制函数
    scenario.earth.rotation(-90)  # 让地球绕z轴旋转90度，格林尼治点对准X轴方向
    plot_earth_fixed(scenario.earth, ax)

    # 修复4：在地球之后绘制卫星位置点，确保可见
    for position, color_rgb, show_point in satellite_positions:
        if show_point:
            ax.scatter(position[0], position[1], position[2], 
                      color=color_rgb, marker='o', s=80, zorder=15,
                      edgecolors='white', linewidth=1)

    # 设置图形属性
    ax.set_xlabel('X (km)', fontsize=10)
    ax.set_ylabel('Y (km)', fontsize=10)
    ax.set_zlabel('Z (km)', fontsize=10)
    
    # 设置标题
    title = f"{scenario.name} - Satellite Orbit"
    if scenario.introduction:
        title += f"\n{scenario.introduction}"
    
    # 添加时间信息
    time_info = (f"Time Range: {scenario.start_time.strftime('%Y-%m-%d %H:%M')} - "
                f"{scenario.end_time.strftime('%Y-%m-%d %H:%M')} UTC")
    title += f"\n{time_info}"
    
    ax.set_title(title, fontsize=12, pad=20)
    
    # 只有当有标签要显示时才显示图例
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    
    # 强制设置相等的坐标轴比例
    ax.set_box_aspect([1,1,1])  # 等比例的长宽高

    # 不显示网格
    ax.grid(False)

    # 不显示坐标轴（可选，根据需要调整）
    ax.set_axis_off()
    
    # 设置合适的视角范围
    # 计算所有卫星轨道点的最大范围，用于设置坐标轴
    max_range_all_positions = 6378  # 地球半径，单位为km
    # 遍历所有卫星，找到最大范围
    if len(scenario.satellites) > 0:
        for satellite in scenario.satellites:
            if len(satellite.eph['cartesian']) > 0:
                max_range = np.max(np.linalg.norm(satellite.eph['cartesian'][:, :3], axis=1))
                if max_range > max_range_all_positions:
                    max_range_all_positions = max_range
    max_range = max_range_all_positions * 1.1
    
    # 设置坐标轴范围
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])

    # 修复5：优化视角，使轨道更容易看到
    ax.view_init(elev=20, azim=45)
    
    # 显示图形
    plt.tight_layout()
    
    return fig, ax

def plot_earth_fixed(earth, ax):
    """
    修复版本的地球绘制函数，解决遮挡问题
    
    参数:
    earth: Earth对象
    ax: matplotlib 3D坐标轴对象
    """
    if earth.use_texture and earth.texture_image is not None:
        plot_earth_with_texture_fixed(earth, ax)
    else:
        plot_earth_simple_fixed(earth, ax)


def plot_earth_with_texture_fixed(earth, ax):
    """
    修复版本：使用贴图绘制地球，减少遮挡
    """
    try:
        # 将贴图转换为numpy数组
        texture_array = np.array(earth.texture_image)
        
        # 关键：使用原始坐标计算纹理映射，这样旋转时纹理会保持固定
        lon = np.arctan2(earth.y_original, earth.x_original)
        lat = np.arcsin(np.clip(earth.z_original / earth.radius, -1, 1))
        
        u = (lon + np.pi) / (2 * np.pi)
        v = (-lat + np.pi/2) / np.pi  # 翻转v坐标，修复上下颠倒问题
        
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        
        # 映射到图像像素
        img_height, img_width = texture_array.shape[:2]
        u_pixels = np.clip((u * (img_width - 1)).astype(int), 0, img_width - 1)
        v_pixels = np.clip((v * (img_height - 1)).astype(int), 0, img_height - 1)
        
        # 获取颜色值
        if len(texture_array.shape) == 3:
            colors = texture_array[v_pixels, u_pixels] / 255.0
        else:
            gray_values = texture_array[v_pixels, u_pixels] / 255.0
            colors = np.stack([gray_values, gray_values, gray_values], axis=-1)
        
        # 关键修复：大幅提高透明度，降低zorder
        surface = ax.plot_surface(earth.x, earth.y, earth.z, 
                                 facecolors=colors,
                                 alpha=0.4,  # 提高透明度
                                 antialiased=False,
                                 shade=False)
        
        # 手动设置zorder（如果支持的话）
        try:
            surface.set_zorder(1)  # 设置最低的zorder
        except:
            pass  # 如果不支持zorder，忽略错误
            
    except Exception as e:
        print(f"绘制纹理时出错: {e}，使用默认颜色")
        plot_earth_simple_fixed(earth, ax)

def plot_earth_simple_fixed(earth, ax):
    """
    修复版本：使用简单颜色绘制地球，减少遮挡
    """
    surface = ax.plot_surface(earth.x, earth.y, earth.z, 
                             color='lightblue', 
                             alpha=0.3,  # 提高透明度
                             antialiased=False)
    
    # 手动设置zorder（如果支持的话）
    try:
        surface.set_zorder(1)  # 设置最低的zorder
    except:
        pass  # 如果不支持zorder，忽略错误


def _identify_data_segments(times, max_gap_hours=1.0):
    """
    识别观测数据中的连续段，基于时间间隔判断
    
    参数:
    times (list): datetime对象列表
    max_gap_hours (float): 最大时间间隔（小时），超过此间隔认为是新的数据段
    
    返回:
    list: 数据段列表，每个段包含连续的数据点索引
    """
    if len(times) == 0:
        return []
    
    segments = []
    current_segment = [0]
    max_gap_seconds = max_gap_hours * 3600
    
    for i in range(1, len(times)):
        time_gap = (times[i] - times[i-1]).total_seconds()
        
        if time_gap > max_gap_seconds:
            # 时间间隔过大，结束当前段，开始新段
            segments.append(current_segment)
            current_segment = [i]
        else:
            # 继续当前段
            current_segment.append(i)
    
    # 添加最后一段
    if current_segment:
        segments.append(current_segment)
    
    return segments


def visualize_stations(scenario, projection='PlateCarree', figsize=(15, 8), 
                      show_names=True, show_altitude=True, station_size=100,
                      altitude_colormap='terrain', size_by_altitude=False):
    """
    在二维世界地图上显示所有观测站，包含海拔信息
    
    参数:
    scenario (SatelliteScenario): 卫星场景对象
    projection (str): 地图投影方式，默认为'PlateCarree'
    figsize (tuple): 图形尺寸
    show_names (bool): 是否显示站点名称
    show_altitude (bool): 是否在标签中显示海拔信息
    station_size (int): 观测站标记基础大小
    altitude_colormap (str): 海拔高度颜色映射，默认'terrain'
    size_by_altitude (bool): 是否根据海拔调整标记大小
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    # 图形中的字体全部使用"Arial"
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = 'Arial'
    
    # 选择地图投影
    projection_dict = {
        'PlateCarree': ccrs.PlateCarree(),
        'Robinson': ccrs.Robinson(),
        'Mollweide': ccrs.Mollweide(),
        'Orthographic': ccrs.Orthographic(central_longitude=0)
    }
    
    if projection not in projection_dict:
        projection = 'PlateCarree'
        print(f"Warning: Unsupported projection, using default PlateCarree projection")
    
    proj = projection_dict[projection]
    
    # 创建图形和轴
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=proj)
    
    # 调整子图位置，为标题、底部和colorbar留出空间
    plt.subplots_adjust(top=0.85, bottom=0.1, left=0.05, right=0.9)
    
    # 添加地图要素
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
    
    # 设置全球范围
    if projection in ['PlateCarree', 'Robinson', 'Mollweide']:
        ax.set_global()
        ax.set_extent([-180, 180, -90, 90], ccrs.PlateCarree())
    elif projection == 'Orthographic':
        ax.set_global()
    else:
        ax.set_global()
    
    # 添加网格线
    if projection == 'PlateCarree':
        gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
    else:
        ax.gridlines(alpha=0.5, linestyle='--')
    
    # 收集所有观测站的海拔信息
    stations_data = []
    for station in scenario.ground_stations:
        try:
            lon = station.longitude
            lat = station.latitude
            # 尝试获取海拔信息
            try:
                altitude = station.altitude
            except AttributeError:
                altitude = 0  # 如果没有海拔信息，默认为0
            
            stations_data.append({
                'name': station.name,
                'lon': lon,
                'lat': lat,
                'altitude': altitude
            })
        except AttributeError:
            print(f"Warning: Ground station {station.name} lacks longitude/latitude information")
    
    if not stations_data:
        print("No valid station data found")
        return fig, ax
    
    # 提取海拔数据用于颜色映射
    altitudes = [s['altitude'] for s in stations_data]
    min_alt = min(altitudes)
    max_alt = max(altitudes)
    
    # 创建颜色映射
    import matplotlib.cm as cm
    import matplotlib.colors as colors
    
    if max_alt > min_alt:
        norm = colors.Normalize(vmin=min_alt, vmax=max_alt)
        cmap = cm.get_cmap(altitude_colormap)
    else:
        # 如果所有站点海拔相同，使用单一颜色
        norm = None
        cmap = None
    
    # 绘制地面站
    station_count = 0
    scatter_colors = []
    scatter_sizes = []
    
    for station_data in stations_data:
        try:
            lon = station_data['lon']
            lat = station_data['lat']
            altitude = station_data['altitude']
            name = station_data['name']
            
            # 确定颜色
            if cmap is not None:
                color = cmap(norm(altitude))
            else:
                color = 'red'
            
            # 确定大小
            if size_by_altitude and max_alt > min_alt:
                # 根据海拔调整大小（海拔越高，标记越大）
                size_factor = 0.5 + 1.5 * (altitude - min_alt) / (max_alt - min_alt)
                marker_size = station_size * size_factor
            else:
                marker_size = station_size
            
            # 绘制观测站标记
            scatter = ax.scatter(lon, lat, marker='^', c=[color], s=marker_size, 
                               zorder=5, transform=ccrs.PlateCarree(), 
                               edgecolors='black', linewidth=1, alpha=0.8)
            
            # 显示站点名称和海拔
            if show_names:
                if show_altitude:
                    label_text = f"{name}\n{altitude:.0f}m"
                else:
                    label_text = name
                
                ax.text(lon, lat + 2, label_text, 
                       transform=ccrs.PlateCarree(),
                       fontsize=9, ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3', 
                               facecolor='white', alpha=0.8, edgecolor='gray'),
                       zorder=6)
            
            station_count += 1
            scatter_colors.append(color)
            scatter_sizes.append(marker_size)
            
        except Exception as e:
            print(f"Error plotting station {station_data['name']}: {e}")
    
    # 添加颜色条（如果有高度变化）
    if cmap is not None and station_count > 0:
        # 创建一个虚拟的scatter用于colorbar
        dummy_scatter = ax.scatter([], [], c=[], s=0, cmap=cmap, norm=norm)
        
        # 添加colorbar
        cbar = plt.colorbar(dummy_scatter, ax=ax, shrink=0.6, aspect=30, 
                          pad=0.02, orientation='vertical')
        cbar.set_label('Altitude (m)', rotation=270, labelpad=15, fontsize=10)
        cbar.ax.tick_params(labelsize=9)
    
    # 设置标题
    title = f"{scenario.name} - Ground Stations"
    if scenario.introduction:
        title += f"\n{scenario.introduction}"
    
    if station_count > 0:
        title += f"\nTotal Stations: {station_count}"
        if altitudes:
            title += f" | Altitude Range: {min_alt:.0f}m - {max_alt:.0f}m"
    
    ax.set_title(title, fontsize=12, pad=20)
    
    # 调整布局，确保标题和内容完全显示
    plt.tight_layout(pad=3.0)
    
    return fig, ax


def visualize_ground_track(scenario, projection='PlateCarree', figsize=(15, 8)):
    """
    使用cartopy绘制卫星星下点轨迹的二维世界地图
    
    参数:
    scenario (SatelliteScenario): 卫星场景对象
    projection (str): 地图投影方式，默认为'PlateCarree'
                     可选: 'PlateCarree', 'Robinson', 'Mollweide', 'Orthographic'
    figsize (tuple): 图形尺寸
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    # 图形中的字体全部使用"Arial"
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = 'Arial'
    
    # 选择地图投影
    projection_dict = {
        'PlateCarree': ccrs.PlateCarree(),
        'Robinson': ccrs.Robinson(),
        'Mollweide': ccrs.Mollweide(),
        'Orthographic': ccrs.Orthographic(central_longitude=0)
    }
    
    if projection not in projection_dict:
        projection = 'PlateCarree'
        print(f"Warning: Unsupported projection, using default PlateCarree projection")
    
    proj = projection_dict[projection]
    
    # 创建图形和轴
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=proj)
    
    # 调整子图位置，为标题和底部留出空间
    plt.subplots_adjust(top=0.85, bottom=0.1, left=0.05, right=0.95)
    
    # 添加地图要素
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.3)
    
    # 设置全球范围 - 必须在添加要素之前设置
    if projection in ['PlateCarree', 'Robinson', 'Mollweide']:
        ax.set_global()
        # 也可以明确设置范围
        ax.set_extent([-180, 180, -90, 90], ccrs.PlateCarree())
    elif projection == 'Orthographic':
        ax.set_global()
    else:
        ax.set_global()
    
    # 添加网格线
    if projection == 'PlateCarree':
        gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
    else:
        ax.gridlines(alpha=0.5, linestyle='--')
    
    # 标记是否已经添加了通用的Start和End标签
    start_label_added = False
    end_label_added = False
    
    # 绘制每个卫星的星下点轨迹
    for i, satellite in enumerate(scenario.satellites):
        # 确保卫星有星下点数据
        if len(satellite.ground_track) == 0:
            print(f"Warning: Satellite {satellite.name} has no ground track data, calculating...")
            satellite.calculate_ground_track()
        
        if len(satellite.ground_track) == 0:
            print(f"Warning: Ground track calculation failed for satellite {satellite.name}, skipping")
            continue
        
        # 获取经纬度数据
        ground_track = np.array(satellite.ground_track)
        longitudes = ground_track[:, 0]
        latitudes = ground_track[:, 1]
        
        # 处理跨越180度经线的情况
        lon_segments, lat_segments = _split_track_at_dateline(longitudes, latitudes)
        
        # 获取卫星轨道颜色
        orbit_color = satellite.orbitColor
        if all(0 <= c <= 1 for c in orbit_color):
            color_rgb = orbit_color
        else:
            color_rgb = [c/255 for c in orbit_color]
        
        # 绘制轨迹段（不添加label）
        for lon_seg, lat_seg in zip(lon_segments, lat_segments):
            if len(lon_seg) > 1:  # 只绘制有效的轨迹段
                ax.plot(lon_seg, lat_seg, 
                       color=color_rgb, 
                       linewidth=1.5, 
                       transform=ccrs.PlateCarree())
        
        # 绘制起始点和结束点
        if len(longitudes) > 0:
            # 起始点 (绿色圆圈) - 只在第一次添加label
            start_label = 'Start' if not start_label_added else None
            ax.scatter(longitudes[0], latitudes[0], 
                      marker='o', color='green', s=50, zorder=5,
                      transform=ccrs.PlateCarree(), 
                      label=start_label)
            start_label_added = True
            
            # 结束点 (红色方块) - 只在第一次添加label
            end_label = 'End' if not end_label_added else None
            ax.scatter(longitudes[-1], latitudes[-1], 
                      marker='s', color='red', s=50, zorder=5,
                      transform=ccrs.PlateCarree(),
                      label=end_label)
            end_label_added = True
            
            # 在起始点附近添加卫星名称文本标签
            ax.text(longitudes[0], latitudes[0] + 3, satellite.name, 
                   transform=ccrs.PlateCarree(),
                   fontsize=9, ha='center', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.2', 
                           facecolor='lightgreen', alpha=0.7, edgecolor='green'),
                   zorder=6)
    
    # 绘制地面站（不添加label，使用文本标签）
    for station in scenario.ground_stations:
        try:
            lon = station.longitude
            lat = station.latitude
            # 使用三角形标记绘制地面站
            ax.scatter(lon, lat, marker='^', color='orange', s=100, zorder=5,
                      transform=ccrs.PlateCarree(), 
                      edgecolors='black', linewidth=1)
            
            # 在地面站旁边添加名称文本标签
            ax.text(lon + 2, lat, station.name, 
                   transform=ccrs.PlateCarree(),
                   fontsize=9, ha='left', va='center',
                   bbox=dict(boxstyle='round,pad=0.2', 
                           facecolor='lightyellow', alpha=0.7, edgecolor='orange'),
                   zorder=6)
            
        except AttributeError:
            print(f"Warning: Ground station {station.name} lacks longitude/latitude information")
    
    # 设置标题
    title = f"{scenario.name} - Satellite Ground Track"
    if scenario.introduction:
        title += f"\n{scenario.introduction}"
    
    # 添加时间信息
    time_info = (f"Time Range: {scenario.start_time.strftime('%Y-%m-%d %H:%M')} - "
                f"{scenario.end_time.strftime('%Y-%m-%d %H:%M')} UTC")
    title += f"\n{time_info}"
    
    ax.set_title(title, fontsize=12, pad=20)
    
    # 只显示Start和End的图例
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(loc='lower left', bbox_to_anchor=(0, 1))

    # 调整布局，确保标题和内容完全显示
    plt.tight_layout(pad=3.0)
    
    return fig, ax


def _split_track_at_dateline(longitudes, latitudes, threshold=180):
    """
    处理跨越日界线(180度经线)的轨迹，将其分割为多个连续段
    
    参数:
    longitudes (array): 经度数组
    latitudes (array): 纬度数组
    threshold (float): 分割阈值，默认为180度
    
    返回:
    tuple: (经度段列表, 纬度段列表)
    """
    if len(longitudes) == 0:
        return [], []
    
    lon_segments = []
    lat_segments = []
    
    current_lon = [longitudes[0]]
    current_lat = [latitudes[0]]
    
    for i in range(1, len(longitudes)):
        # 检查是否跨越日界线
        lon_diff = abs(longitudes[i] - longitudes[i-1])
        
        if lon_diff > threshold:
            # 跨越日界线，结束当前段
            if len(current_lon) > 1:
                lon_segments.append(np.array(current_lon))
                lat_segments.append(np.array(current_lat))
            
            # 开始新的段
            current_lon = [longitudes[i]]
            current_lat = [latitudes[i]]
        else:
            # 继续当前段
            current_lon.append(longitudes[i])
            current_lat.append(latitudes[i])
    
    # 添加最后一段
    if len(current_lon) > 0:
        lon_segments.append(np.array(current_lon))
        lat_segments.append(np.array(current_lat))
    
    return lon_segments, lat_segments


def save_ground_track_data(scenario, filename):
    """
    保存所有卫星的星下点数据到文件
    
    参数:
    scenario (SatelliteScenario): 卫星场景对象
    filename (str): 输出文件名
    """
    with open(filename, 'w') as f:
        f.write("# Satellite Ground Track Data\n")
        f.write(f"# Scenario: {scenario.name}\n")
        f.write(f"# Time Range: {scenario.start_time} - {scenario.end_time}\n")
        f.write("# Format: Satellite Name, Time, Longitude(deg), Latitude(deg)\n")
        
        for satellite in scenario.satellites:
            if len(satellite.ground_track) > 0:
                for i, (time_point, ground_point) in enumerate(
                    zip(satellite.eph['time'], satellite.ground_track)):
                    f.write(f"{satellite.name}, {time_point.isoformat()}, "
                           f"{ground_point[0]:.6f}, {ground_point[1]:.6f}\n")
    
    print(f"Ground track data saved to {filename}")
    

def visualize_access(access_obj, figsize=(12, 8), show_grid=True):
    """
    可视化观测数据的主函数
    
    根据观测数据类型，调用不同的函数实现画图
    
    参数:
    access_obj (Access): 观测对象
    figsize (tuple): 图形尺寸
    show_grid (bool): 是否显示网格
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    # 图形中的字体全部使用"Arial"
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = 'Arial'
    
    if len(access_obj.data) == 0:
        print("警告: 观测对象中没有数据可显示")
        return None, None
    
    # 根据观测类型调用相应的可视化函数
    if access_obj.obs_type == 'Azi_Ele':
        return visualize_azi_ele(access_obj, figsize, show_grid)
    elif access_obj.obs_type == 'RA_DEC':
        return visualize_ra_dec(access_obj, figsize, show_grid)
    elif access_obj.obs_type == 'R_RD':
        return visualize_r_rd(access_obj, figsize, show_grid)
    else:
        print(f"不支持的观测类型: {access_obj.obs_type}")
        return None, None


def visualize_azi_ele(access_obj, figsize=(12, 8), show_grid=True):
    """
    可视化方位角俯仰角观测数据
    
    参数:
    access_obj (Access): 观测对象
    figsize (tuple): 图形尺寸
    show_grid (bool): 是否显示网格
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    fig = plt.figure(figsize=figsize)
    
    # 创建2x2的子图布局，调整间距避免重叠
    plt.subplots_adjust(top=0.85, bottom=0.1, left=0.1, right=0.95, hspace=0.4, wspace=0.3)
    
    # 1. 时间序列图 - 方位角
    ax1 = plt.subplot(2, 2, 1)
    # 2. 时间序列图 - 俯仰角
    ax2 = plt.subplot(2, 2, 2)
    # 3. 方位角vs俯仰角散点图
    ax3 = plt.subplot(2, 2, 3)
    # 4. 天空图（极坐标）
    ax4 = plt.subplot(2, 2, 4, projection='polar')
    
    # 提取数据
    times = access_obj.times
    data = np.array(access_obj.data)
    azimuths = data[:, 0]
    elevations = data[:, 1]
    
    # 识别数据段（基于时间间隔）
    segments = _identify_data_segments(times, max_gap_hours=1.0)
    
    # 使用更好看的颜色
    magenta_color = [204/255, 121/255, 167/255]  # Magenta
    teal_color = [0/255, 158/255, 115/255]       # Teal
    
    # 1. 方位角时间序列 - 分段绘制，使用新颜色
    for segment in segments:
        segment_times = [times[i] for i in segment]
        segment_azimuths = azimuths[segment]
        ax1.plot(segment_times, segment_azimuths, color=magenta_color, linewidth=2, marker='o', markersize=5)
    
    ax1.set_ylabel('Azimuth (deg)', fontsize=11)
    ax1.set_title(f'Azimuth vs Time\n{access_obj.station_id} → {access_obj.satellite_id}', fontsize=10)
    ax1.grid(show_grid)
    ax1.set_ylim(0, 360)
    
    # 2. 俯仰角时间序列 - 分段绘制，使用新颜色
    for segment in segments:
        segment_times = [times[i] for i in segment]
        segment_elevations = elevations[segment]
        ax2.plot(segment_times, segment_elevations, color=teal_color, linewidth=2, marker='s', markersize=5)
    
    ax2.set_ylabel('Elevation (deg)', fontsize=11)
    ax2.set_title('Elevation vs Time', fontsize=10)
    ax2.grid(show_grid)
    ax2.set_ylim(0, 90)
    
    # 3. 方位角vs俯仰角散点图 - 只画点，不画线
    scatter = ax3.scatter(azimuths, elevations, c=range(len(times)), 
                         cmap='viridis', s=30, alpha=0.8, zorder=2)
    
    # 标记起点和终点
    if len(azimuths) > 0:
        ax3.scatter(azimuths[0], elevations[0], marker='o', s=120, color='green', 
                   label='Start', zorder=3, edgecolor='white', linewidth=2)
        ax3.scatter(azimuths[-1], elevations[-1], marker='s', s=120, color='red', 
                   label='End', zorder=3, edgecolor='white', linewidth=2)
    
    ax3.set_xlabel('Azimuth (deg)', fontsize=11)
    ax3.set_ylabel('Elevation (deg)', fontsize=11)
    ax3.set_title('Azimuth vs Elevation', fontsize=10)
    ax3.grid(show_grid)
    ax3.set_xlim(0, 360)
    ax3.set_ylim(0, 90)
    ax3.legend(fontsize=9)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax3, shrink=0.8)
    cbar.set_label('Time Index', fontsize=10)
    
    # 4. 天空图（极坐标图）- 增强版
    # 转换到极坐标：极径=90-俯仰角，极角=方位角
    theta = np.radians(azimuths)  # 方位角转弧度
    r = 90 - elevations  # 天顶距（90度减去俯仰角）
    
    # 分段绘制天空轨迹，段内连线，段间不连线
    for segment in segments:
        segment_theta = theta[segment]
        segment_r = r[segment]
        if len(segment_theta) > 1:  # 只有多个点才画线
            ax4.plot(segment_theta, segment_r, 'g-', linewidth=2, alpha=0.8)
        ax4.scatter(segment_theta, segment_r, c=np.array(segment), cmap='plasma', s=25)
    
    # 标记起始和结束点
    if len(theta) > 0:
        ax4.scatter(theta[0], r[0], marker='o', s=120, color='green', 
                   label='Start', zorder=5, edgecolor='white', linewidth=2)
        ax4.scatter(theta[-1], r[-1], marker='s', s=120, color='red', 
                   label='End', zorder=5, edgecolor='white', linewidth=2)
    
    # 设置天空图的基本参数
    ax4.set_ylim(0, 90)
    ax4.set_theta_zero_location('N')  # 北方为0度
    ax4.set_theta_direction(-1)  # 顺时针方向
    ax4.set_title('Sky Track (Polar View)', pad=20, fontsize=10)
    
    # 设置方位角刻度标签，在角度后添加方位信息
    ax4.set_thetagrids([0, 90, 180, 270], ['0° (N)', '90° (E)', '180° (S)', '270° (W)'])
    
    # 标记地平线和重要仰角圈
    ax4.set_rticks([0, 30, 60, 90])
    ax4.set_rgrids([0, 30, 60, 90], ['90°\n(Zenith)', '60°', '30°', '0°'])
    
    # 添加仰角圈的视觉增强
    elevation_circles = [0, 30, 60]  # 地平线、30°、60°
    circle_theta = np.linspace(0, 2*np.pi, 100)
    
    for elev in elevation_circles:
        circle_r = 90 - elev
        if elev == 0:  # 地平线 - 用棕色粗线
            ax4.plot(circle_theta, [circle_r]*len(circle_theta), color='brown', 
                    linewidth=3, alpha=0.8, label='Horizon')
        else:
            ax4.plot(circle_theta, [circle_r]*len(circle_theta), 'k--', 
                    linewidth=1, alpha=0.3)
    
    # 天顶用灰色五角星表示
    ax4.scatter(0, 0, marker='*', s=200, color='gray', 
               label='Zenith', zorder=6, edgecolor='black', linewidth=1)
    
    ax4.set_rlabel_position(135)  # 调整径向标签位置避免与方位标记重叠
    ax4.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0), fontsize=9)
    
    # 添加总标题，调整位置避免重叠
    fig.suptitle(f'Azimuth-Elevation Observation Data\n'
                f'Station: {access_obj.station_id}, Satellite: {access_obj.satellite_id}\n'
                f'Data Points: {len(times)} (in {len(segments)} segments)', 
                fontsize=12, y=0.95)
    
    return fig, [ax1, ax2, ax3, ax4]


def visualize_ra_dec(access_obj, figsize=(12, 8), show_grid=True):
    """
    可视化赤经赤纬观测数据
    
    参数:
    access_obj (Access): 观测对象
    figsize (tuple): 图形尺寸
    show_grid (bool): 是否显示网格
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    fig = plt.figure(figsize=figsize)
    
    # 调整间距避免重叠
    plt.subplots_adjust(top=0.85, bottom=0.1, left=0.1, right=0.95, hspace=0.4, wspace=0.3)
    
    # 创建2x2的子图布局
    ax1 = plt.subplot(2, 2, 1)  # 赤经时间序列
    ax2 = plt.subplot(2, 2, 2)  # 赤纬时间序列
    ax3 = plt.subplot(2, 2, 3)  # 赤经vs赤纬散点图
    ax4 = plt.subplot(2, 2, 4)  # 天球投影图
    
    # 提取数据
    times = access_obj.times
    data = np.array(access_obj.data)
    ra = data[:, 0]   # 赤经
    dec = data[:, 1]  # 赤纬
    
    # 识别数据段（基于时间间隔）
    segments = _identify_data_segments(times, max_gap_hours=1.0)
    
    # 使用更好看的颜色
    magenta_color = [204/255, 121/255, 167/255]  # Magenta
    teal_color = [0/255, 158/255, 115/255]       # Teal
    
    # 1. 赤经时间序列 - 分段绘制，使用新颜色
    for segment in segments:
        segment_times = [times[i] for i in segment]
        segment_ra = ra[segment]
        ax1.plot(segment_times, segment_ra, color=magenta_color, linewidth=2, marker='o', markersize=5)
    
    ax1.set_ylabel('Right Ascension (deg)', fontsize=11)
    ax1.set_title(f'RA vs Time\n{access_obj.station_id} → {access_obj.satellite_id}', fontsize=10)
    ax1.grid(show_grid)
    ax1.set_ylim(0, 360)
    
    # 2. 赤纬时间序列 - 分段绘制，使用新颜色
    for segment in segments:
        segment_times = [times[i] for i in segment]
        segment_dec = dec[segment]
        ax2.plot(segment_times, segment_dec, color=teal_color, linewidth=2, marker='s', markersize=5)
    
    ax2.set_ylabel('Declination (deg)', fontsize=11)
    ax2.set_title('DEC vs Time', fontsize=10)
    ax2.grid(show_grid)
    ax2.set_ylim(-90, 90)
    
    # 3. 赤经vs赤纬散点图 - 只画点，不画线
    scatter = ax3.scatter(ra, dec, c=range(len(times)), 
                         cmap='viridis', s=30, alpha=0.8, zorder=2)
    
    # 标记起点和终点
    if len(ra) > 0:
        ax3.scatter(ra[0], dec[0], marker='o', s=120, color='green', 
                   label='Start', zorder=3, edgecolor='white', linewidth=2)
        ax3.scatter(ra[-1], dec[-1], marker='s', s=120, color='red', 
                   label='End', zorder=3, edgecolor='white', linewidth=2)
    
    ax3.set_xlabel('Right Ascension (deg)', fontsize=11)
    ax3.set_ylabel('Declination (deg)', fontsize=11)
    ax3.set_title('RA vs DEC', fontsize=10)
    ax3.grid(show_grid)
    ax3.set_xlim(0, 360)
    ax3.set_ylim(-90, 90)
    ax3.legend(fontsize=9)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax3, shrink=0.8)
    cbar.set_label('Time Index', fontsize=10)
    
    # 4. 天球投影图（等面积投影）
    # 使用Mollweide投影显示天球坐标
    ra_rad = np.radians(ra - 180)  # 转换为[-180, 180]区间并转弧度
    dec_rad = np.radians(dec)
    
    # 分段绘制天球轨迹
    for segment in segments:
        segment_ra_rad = ra_rad[segment]
        segment_dec_rad = dec_rad[segment]
        if len(segment_ra_rad) > 1:
            ax4.plot(segment_ra_rad, segment_dec_rad, 'g-', linewidth=2, alpha=0.8)
        ax4.scatter(segment_ra_rad, segment_dec_rad, c=np.array(segment), 
                   cmap='plasma', s=25)
    
    # 标记起始和结束点
    if len(ra_rad) > 0:
        ax4.scatter(ra_rad[0], dec_rad[0], marker='o', s=120, color='green', 
                   label='Start', zorder=5, edgecolor='white', linewidth=2)
        ax4.scatter(ra_rad[-1], dec_rad[-1], marker='s', s=120, color='red', 
                   label='End', zorder=5, edgecolor='white', linewidth=2)
    
    ax4.set_xlabel('RA (radians, centered at 180°)', fontsize=11)
    ax4.set_ylabel('DEC (radians)', fontsize=11)
    ax4.set_title('Celestial Track', fontsize=10)
    ax4.grid(show_grid)
    ax4.legend(fontsize=9)
    
    # 设置坐标轴范围
    ax4.set_xlim(-np.pi, np.pi)
    ax4.set_ylim(-np.pi/2, np.pi/2)
    
    # 添加总标题，调整位置避免重叠
    fig.suptitle(f'Right Ascension - Declination Observation Data\n'
                f'Station: {access_obj.station_id}, Satellite: {access_obj.satellite_id}\n'
                f'Data Points: {len(times)} (in {len(segments)} segments)', 
                fontsize=12, y=0.95)
    
    return fig, [ax1, ax2, ax3, ax4]


def visualize_r_rd(access_obj, figsize=(12, 8), show_grid=True):
    """
    可视化测距测速观测数据
    
    参数:
    access_obj (Access): 观测对象
    figsize (tuple): 图形尺寸
    show_grid (bool): 是否显示网格
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    fig = plt.figure(figsize=figsize)
    
    # 调整间距避免重叠
    plt.subplots_adjust(top=0.85, bottom=0.1, left=0.1, right=0.95, hspace=0.4, wspace=0.3)
    
    # 创建2x2的子图布局
    ax1 = plt.subplot(2, 2, 1)  # 距离时间序列
    ax2 = plt.subplot(2, 2, 2)  # 距离变化率时间序列
    ax3 = plt.subplot(2, 2, 3)  # 距离vs距离变化率
    ax4 = plt.subplot(2, 2, 4)  # 距离和距离变化率的双y轴图
    
    # 提取数据
    times = access_obj.times
    data = np.array(access_obj.data)
    ranges = data[:, 0]      # 距离 (km)
    range_rates = data[:, 1] # 距离变化率 (km/s)
    
    # 识别数据段（基于时间间隔）
    segments = _identify_data_segments(times, max_gap_hours=1.0)
    
    # 使用更好看的颜色
    magenta_color = [204/255, 121/255, 167/255]  # Magenta
    teal_color = [0/255, 158/255, 115/255]       # Teal
    
    # 1. 距离时间序列 - 分段绘制，使用新颜色
    for segment in segments:
        segment_times = [times[i] for i in segment]
        segment_ranges = ranges[segment]
        ax1.plot(segment_times, segment_ranges, color=magenta_color, linewidth=2, marker='o', markersize=5)
    
    ax1.set_ylabel('Range (km)', fontsize=11)
    ax1.set_title(f'Range vs Time\n{access_obj.station_id} → {access_obj.satellite_id}', fontsize=10)
    ax1.grid(show_grid)
    
    # 2. 距离变化率时间序列 - 分段绘制，使用新颜色
    for segment in segments:
        segment_times = [times[i] for i in segment]
        segment_rates = range_rates[segment]
        ax2.plot(segment_times, segment_rates, color=teal_color, linewidth=2, marker='s', markersize=5)
    
    ax2.set_ylabel('Range Rate (km/s)', fontsize=11)
    ax2.set_title('Range Rate vs Time', fontsize=10)
    ax2.grid(show_grid)
    
    # 添加零线
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    # 3. 距离vs距离变化率散点图 - 只画点，不画线
    scatter = ax3.scatter(ranges, range_rates, c=range(len(times)), 
                         cmap='viridis', s=40, alpha=0.8, zorder=2)
    
    # 标记起点和终点
    if len(ranges) > 0:
        ax3.scatter(ranges[0], range_rates[0], marker='o', s=120, color='green', 
                   label='Start', zorder=3, edgecolor='white', linewidth=2)
        ax3.scatter(ranges[-1], range_rates[-1], marker='s', s=120, color='red', 
                   label='End', zorder=3, edgecolor='white', linewidth=2)
    
    ax3.set_xlabel('Range (km)', fontsize=11)
    ax3.set_ylabel('Range Rate (km/s)', fontsize=11)
    ax3.set_title('Range vs Range Rate', fontsize=10)
    ax3.grid(show_grid)
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax3.legend(fontsize=9)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax3, shrink=0.8)
    cbar.set_label('Time Index', fontsize=10)
    
    # 4. 双y轴时间序列图 - 分段绘制
    ax4_twin = ax4.twinx()
    
    # 分段绘制距离和距离变化率
    for i, segment in enumerate(segments):
        segment_times = [times[j] for j in segment]
        segment_ranges = ranges[segment]
        segment_rates = range_rates[segment]
        
        # 只在第一段添加标签
        range_label = 'Range' if i == 0 else None
        rate_label = 'Range Rate' if i == 0 else None
        
        ax4.plot(segment_times, segment_ranges, color=magenta_color, linewidth=2, 
                label=range_label, marker='o', markersize=4)
        ax4_twin.plot(segment_times, segment_rates, color=teal_color, linewidth=2, 
                     label=rate_label, marker='s', markersize=4)
    
    ax4.set_xlabel('Time', fontsize=11)
    ax4.set_ylabel('Range (km)', color=magenta_color, fontsize=11)
    ax4_twin.set_ylabel('Range Rate (km/s)', color=teal_color, fontsize=11)
    ax4.set_title('Range and Range Rate vs Time', fontsize=10)
    
    ax4.tick_params(axis='y', labelcolor=magenta_color)
    ax4_twin.tick_params(axis='y', labelcolor=teal_color)
    ax4.grid(show_grid)
    ax4_twin.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    # 合并图例
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
    
    # 添加总标题，调整位置避免重叠
    fig.suptitle(f'Range and Range Rate Observation Data\n'
                f'Station: {access_obj.station_id}, Satellite: {access_obj.satellite_id}\n'
                f'Data Points: {len(times)} (in {len(segments)} segments)', 
                fontsize=12, y=0.95)
    
    # 计算统计信息并添加文本
    min_range, max_range = ranges.min(), ranges.max()
    min_rate, max_rate = range_rates.min(), range_rates.max()
    
    stats_text = (f'Range: {min_range:.1f} - {max_range:.1f} km\n'
                 f'Rate: {min_rate:.3f} - {max_rate:.3f} km/s')
    
    fig.text(0.02, 0.02, stats_text, fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    return fig, [ax1, ax2, ax3, ax4]


def visualize_multiple_access(access_list, obs_type_filter=None, figsize=(15, 10)):
    """
    同时可视化多个观测对象的数据对比
    
    参数:
    access_list (list): Access对象列表
    obs_type_filter (str): 只显示特定类型的观测，None表示显示所有
    figsize (tuple): 图形尺寸
    
    返回:
    tuple: (fig, ax) matplotlib图形对象和轴对象
    """
    # 图形中的字体全部使用"Arial"
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = 'Arial'
    
    # 过滤观测对象
    if obs_type_filter:
        filtered_access = [acc for acc in access_list if acc.obs_type == obs_type_filter]
    else:
        filtered_access = access_list
    
    if len(filtered_access) == 0:
        print("没有符合条件的观测数据")
        return None, None
    
    # 按观测类型分组
    grouped_access = {}
    for acc in filtered_access:
        if acc.obs_type not in grouped_access:
            grouped_access[acc.obs_type] = []
        grouped_access[acc.obs_type].append(acc)
    
    # 创建子图
    n_types = len(grouped_access)
    fig, axes = plt.subplots(n_types, 1, figsize=figsize)
    if n_types == 1:
        axes = [axes]
    
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    for i, (obs_type, acc_list) in enumerate(grouped_access.items()):
        ax = axes[i]
        
        for j, acc in enumerate(acc_list):
            if len(acc.data) == 0:
                continue
                
            times = acc.times
            data = np.array(acc.data)
            color = colors[j % len(colors)]
            label = f"{acc.station_id}-{acc.satellite_id}"
            
            if obs_type == 'Azi_Ele':
                ax.plot(times, data[:, 1], color=color, label=f"{label} (Elevation)", 
                       linewidth=2, marker='o', markersize=3)
                ax.set_ylabel('Elevation (deg)')
                ax.set_title(f'Elevation Comparison - {obs_type}')
                
            elif obs_type == 'RA_DEC':
                ax.plot(times, data[:, 1], color=color, label=f"{label} (DEC)", 
                       linewidth=2, marker='s', markersize=3)
                ax.set_ylabel('Declination (deg)')
                ax.set_title(f'Declination Comparison - {obs_type}')
                
            elif obs_type == 'R_RD':
                ax.plot(times, data[:, 0], color=color, label=f"{label} (Range)", 
                       linewidth=2, marker='^', markersize=3)
                ax.set_ylabel('Range (km)')
                ax.set_title(f'Range Comparison - {obs_type}')
        
        ax.grid(True)
        ax.legend()
        
        if i == len(grouped_access) - 1:
            ax.set_xlabel('Time')
    
    plt.tight_layout()
    
    # 添加总标题
    fig.suptitle(f'Multiple Access Data Comparison\n'
                f'Total Observations: {len(filtered_access)}', 
                fontsize=16, y=0.98)
    
    return fig, axes