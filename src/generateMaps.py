#!/usr/bin/env python3
"""
World Map Generator - Clean Style with Multiple Color Schemes
生成干净的世界地图平面图，提供多种颜色风格
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings
import os

# 忽略cartopy的警告信息
warnings.filterwarnings('ignore')

def get_color_styles():
    """
    定义不同的颜色风格配置
    
    返回:
    dict: 包含各种风格配置的字典
    """
    styles = {
        'classic': {
            'name': 'Classic',
            'land_color': 'lightgray',
            'land_alpha': 0.3,
            'ocean_color': 'lightblue', 
            'ocean_alpha': 0.3,
            'coastline_color': 'black',
            'coastline_width': 0.5,
            'border_color': 'gray',
            'border_width': 0.3,
            'background': 'white'
        },
        
        'dark': {
            'name': 'Dark Theme',
            'land_color': '#2F4F4F',  # DarkSlateGray
            'land_alpha': 0.8,
            'ocean_color': '#191970',  # MidnightBlue
            'ocean_alpha': 0.8,
            'coastline_color': '#F0F8FF',  # AliceBlue
            'coastline_width': 0.6,
            'border_color': '#708090',  # SlateGray
            'border_width': 0.4,
            'background': '#1C1C1C'  # Dark background
        },
        
        'minimalist': {
            'name': 'Minimalist',
            'land_color': '#F5F5F5',  # WhiteSmoke
            'land_alpha': 1.0,
            'ocean_color': '#FFFFFF',  # White
            'ocean_alpha': 1.0,
            'coastline_color': '#696969',  # DimGray
            'coastline_width': 0.4,
            'border_color': '#D3D3D3',  # LightGray
            'border_width': 0.2,
            'background': 'white'
        },
        
        'natural': {
            'name': 'Natural',
            'land_color': '#DEB887',  # BurlyWood
            'land_alpha': 0.7,
            'ocean_color': '#4682B4',  # SteelBlue
            'ocean_alpha': 0.6,
            'coastline_color': '#8B4513',  # SaddleBrown
            'coastline_width': 0.5,
            'border_color': '#A0522D',  # Sienna
            'border_width': 0.3,
            'background': '#F0F8FF'  # AliceBlue
        },
        
        'high_contrast': {
            'name': 'High Contrast',
            'land_color': '#000000',  # Black
            'land_alpha': 1.0,
            'ocean_color': '#FFFFFF',  # White
            'ocean_alpha': 1.0,
            'coastline_color': '#FF0000',  # Red
            'coastline_width': 0.8,
            'border_color': '#FF0000',  # Red
            'border_width': 0.5,
            'background': '#FFFFFF'
        },
        
        'vintage': {
            'name': 'Vintage',
            'land_color': '#F4A460',  # SandyBrown
            'land_alpha': 0.8,
            'ocean_color': '#B0C4DE',  # LightSteelBlue
            'ocean_alpha': 0.7,
            'coastline_color': '#8B4513',  # SaddleBrown
            'coastline_width': 0.6,
            'border_color': '#CD853F',  # Peru
            'border_width': 0.4,
            'background': '#FDF5E6'  # OldLace
        },
        
        'arctic': {
            'name': 'Arctic',
            'land_color': '#F0F8FF',  # AliceBlue
            'land_alpha': 0.9,
            'ocean_color': '#4169E1',  # RoyalBlue
            'ocean_alpha': 0.4,
            'coastline_color': '#191970',  # MidnightBlue
            'coastline_width': 0.5,
            'border_color': '#4682B4',  # SteelBlue
            'border_width': 0.3,
            'background': '#F8F8FF'  # GhostWhite
        },
        
        'earth_tones': {
            'name': 'Earth Tones',
            'land_color': '#D2B48C',  # Tan
            'land_alpha': 0.7,
            'ocean_color': '#008B8B',  # DarkCyan
            'ocean_alpha': 0.5,
            'coastline_color': '#8B4513',  # SaddleBrown
            'coastline_width': 0.5,
            'border_color': '#A0522D',  # Sienna
            'border_width': 0.3,
            'background': '#FFFAF0'  # FloralWhite
        }
    }
    
    return styles

def generate_world_map(style='classic', 
                      output_filename=None,
                      figsize=(10, 6), 
                      dpi=30):
    """
    生成指定风格的世界地图并保存到data目录
    
    参数:
    style (str): 风格名称，默认'classic'
    output_filename (str): 输出文件名，如果为None则自动生成
    figsize (tuple): 图形尺寸，默认(10, 6)
    dpi (int): 分辨率，默认30
    """
    
    # 确保data目录存在
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created 'data' directory")
    
    # 获取风格配置
    styles = get_color_styles()
    if style not in styles:
        print(f"Warning: Style '{style}' not found, using 'classic'")
        style = 'classic'
    
    style_config = styles[style]
    
    # 生成输出文件名
    if output_filename is None:
        output_filename = f"data/world_map_{style}.jpg"
    else:
        output_filename = f"data/{output_filename}"
    
    # 设置字体
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.sans-serif'] = 'Arial'
    
    # 使用PlateCarree投影
    proj = ccrs.PlateCarree()
    
    # 创建图形，不显示坐标轴
    fig = plt.figure(figsize=figsize, frameon=False, facecolor=style_config['background'])
    ax = plt.axes(projection=proj)
    
    # 移除所有边框和坐标轴
    ax.set_frame_on(False)
    ax.axis('off')
    
    # 设置全球范围
    ax.set_global()
    ax.set_extent([-180, 180, -90, 90], ccrs.PlateCarree())
    
    # 设置背景色 - 修正方法
    fig.patch.set_facecolor(style_config['background'])
    
    # 添加地图要素（使用风格配置）
    ax.add_feature(cfeature.OCEAN, 
                   color=style_config['ocean_color'], 
                   alpha=style_config['ocean_alpha'])
    
    ax.add_feature(cfeature.LAND, 
                   color=style_config['land_color'], 
                   alpha=style_config['land_alpha'])
    
    ax.add_feature(cfeature.COASTLINE, 
                   linewidth=style_config['coastline_width'], 
                   color=style_config['coastline_color'])
    
    ax.add_feature(cfeature.BORDERS, 
                   linewidth=style_config['border_width'], 
                   color=style_config['border_color'])
    
    # 调整图形布局，去除所有边距
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    # 保存图片
    print(f"Generating {style_config['name']} style world map...")
    
    plt.savefig(output_filename, 
                format='jpeg',
                dpi=dpi, 
                bbox_inches='tight',
                pad_inches=0,
                facecolor=style_config['background'],
                edgecolor='none')
    
    print(f"Saved: {output_filename}")
    print(f"Resolution: {figsize[0]*dpi} x {figsize[1]*dpi} pixels")
    
    # 关闭图形释放内存
    plt.close()

def generate_all_styles():
    """
    生成所有风格的世界地图
    """
    styles = get_color_styles()
    
    print(f"Generating {len(styles)} different style maps...")
    print("=" * 60)
    
    for style_name in styles.keys():
        generate_world_map(style=style_name)
        print()  # 空行分隔
    
    return list(styles.keys())

def list_available_styles():
    """
    列出所有可用的风格
    """
    styles = get_color_styles()
    print("Available Styles:")
    print("-" * 40)
    for style_name, config in styles.items():
        print(f"• {style_name:15} - {config['name']}")

if __name__ == "__main__":
    print("World Map Generator - Clean Style Edition")
    print("=" * 60)
    
    # 显示可用风格
    list_available_styles()
    print()
    
    # 生成所有风格的地图
    generated_styles = generate_all_styles()
    
    print("=" * 60)
    print("All maps generated successfully!")
    print(f"\nGenerated {len(generated_styles)} maps in 'data/' directory:")
    
    for style in generated_styles:
        print(f"- world_map_{style}.jpg")
    
    print(f"\nAll maps use PlateCarree projection")
    print(f"Resolution: 6000 x 3600 pixels (300 DPI)")
    print(f"Format: JPEG")