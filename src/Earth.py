import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

class Earth:
    """
    简化的地球类，用于绘制带纹理的地球模型
    """
    
    def __init__(self, texture_path='data/world_map_arctic.jpg', 
                 radius=6371.0, resolution=50, use_texture=True):
        """
        初始化地球对象
        
        参数:
        texture_path (str): 地球贴图文件路径
        radius (float): 地球半径，单位km，默认6371km
        resolution (int): 地球表面网格分辨率，默认50
        use_texture (bool): 是否使用贴图，默认True
        """
        self.texture_path = texture_path
        self.radius = radius
        self.resolution = resolution
        self.use_texture = use_texture
        self.texture_image = None
        
        # 加载贴图
        if self.use_texture:
            self.load_texture()
        
        # 生成地球球面坐标
        self.generate_sphere()
    
    def load_texture(self):
        """
        加载地球贴图
        """
        try:
            if os.path.exists(self.texture_path):
                self.texture_image = Image.open(self.texture_path)
            else:
                print(f"警告: 找不到贴图文件 {self.texture_path}")
                self.texture_image = None
                self.use_texture = False
        except Exception as e:
            print(f"警告: 加载贴图时出错 - {e}")
            self.texture_image = None
            self.use_texture = False
    
    def generate_sphere(self):
        """
        生成地球球面的坐标点
        """
        u = np.linspace(0, 2 * np.pi, self.resolution)
        v = np.linspace(0, np.pi, self.resolution)
        
        # 保存原始坐标，用于旋转计算
        self.x_original = self.radius * np.outer(np.cos(u), np.sin(v))
        self.y_original = self.radius * np.outer(np.sin(u), np.sin(v))
        self.z_original = self.radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # 当前显示坐标（初始时等于原始坐标）
        self.x = self.x_original.copy()
        self.y = self.y_original.copy()
        self.z = self.z_original.copy()
    
    def rotation(self, theta):
        """
        让地球绕z轴旋转theta度
        
        参数:
        theta (float): 旋转角度（度）
        """
        # 将角度转换为弧度
        theta_rad = np.radians(theta)
        
        # 绕z轴旋转矩阵
        cos_theta = np.cos(theta_rad)
        sin_theta = np.sin(theta_rad)
        
        # 应用旋转变换
        self.x = self.x_original * cos_theta - self.y_original * sin_theta
        self.y = self.x_original * sin_theta + self.y_original * cos_theta
        self.z = self.z_original.copy()  # z坐标不变
    
    def plot_earth(self, ax):
        """
        在3D坐标轴上绘制地球
        
        参数:
        ax: matplotlib 3D坐标轴对象
        """
        if self.use_texture and self.texture_image is not None:
            self._plot_earth_with_texture(ax)
        else:
            self._plot_earth_simple(ax)
    
    def _plot_earth_with_texture(self, ax):
        """
        使用贴图绘制地球
        """
        try:
            # 将贴图转换为numpy数组
            texture_array = np.array(self.texture_image)
            
            # 关键：使用原始坐标计算纹理映射，这样旋转时纹理会保持固定
            lon = np.arctan2(self.y_original, self.x_original)
            lat = np.arcsin(np.clip(self.z_original / self.radius, -1, 1))
            
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
            
            # 绘制地球 - 兼容性修复：移除不支持的参数
            surface = ax.plot_surface(self.x, self.y, self.z, 
                                     facecolors=colors,
                                     alpha=0.7,  # 降低透明度，减少遮挡
                                     antialiased=False,
                                     shade=False)
            
            # 手动设置zorder（如果支持的话）
            try:
                surface.set_zorder(1)  # 设置较低的zorder
            except:
                pass  # 如果不支持zorder，忽略错误
            
        except Exception as e:
            print(f"绘制纹理时出错: {e}，使用默认颜色")
            self._plot_earth_simple(ax)
    
    def _plot_earth_simple(self, ax):
        """
        使用简单颜色绘制地球
        """
        surface = ax.plot_surface(self.x, self.y, self.z, 
                                 color='lightblue', 
                                 alpha=0.6,  # 降低透明度，减少遮挡
                                 antialiased=False)
        
        # 手动设置zorder（如果支持的话）
        try:
            surface.set_zorder(1)  # 设置较低的zorder
        except:
            pass  # 如果不支持zorder，忽略错误

# 使用示例
if __name__ == "__main__":
    from mpl_toolkits.mplot3d import Axes3D
    
    # 创建地球对象
    earth = Earth()
    
    # 让地球绕z轴旋转90度（更明显的旋转效果）
    earth.rotation(90)
    
    # 创建3D图形
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制地球
    earth.plot_earth(ax)
    
    # 设置坐标轴
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('Earth (Rotated 90° around Z-axis)')
    
    # 设置相等的坐标轴比例和范围
    ax.grid(False)
    
    # 使用地球半径的1.5倍作为显示范围，确保比例正确
    limit = earth.radius * 1.5
    ax.set_xlim([-limit, limit])
    ax.set_ylim([-limit, limit])
    ax.set_zlim([-limit, limit])
    
    # 强制设置相等的坐标轴比例
    ax.set_box_aspect([1,1,1])  # 等比例的长宽高
    
    # 优化3D渲染（兼容性处理）
    try:
        ax.computed_zorder = False
    except AttributeError:
        pass
    
    plt.tight_layout()
    plt.show()