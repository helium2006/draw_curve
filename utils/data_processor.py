#!/usr/bin/env python3
"""
data_processor.py
数据处理工具，包括曲线平滑算法
"""

import numpy as np
from scipy import interpolate


def parse_input_data(input_text: str) -> tuple[list[float], list[float]]:
    """
    解析用户输入的(x,y)数据
    
    Args:
        input_text: 包含(x,y)数据的文本
    
    Returns:
        x_list, y_list: x和y的浮点数列表
    
    Raises:
        ValueError: 如果数据格式不正确
    """
    x_list = []
    y_list = []
    
    # 按行分割输入
    lines = input_text.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            # 尝试多种分隔符
            parts = []
            for sep in [' ', ',', '\t', ';']:
                parts = line.split(sep)
                if len(parts) >= 2:
                    break
            
            if len(parts) < 2:
                raise ValueError(f"第{line_num}行格式错误: {line}")
            
            x = float(parts[0])
            y = float(parts[1])
            x_list.append(x)
            y_list.append(y)
        except ValueError as e:
            raise ValueError(f"第{line_num}行解析错误: {str(e)}")
    
    if len(x_list) < 2:
        raise ValueError("至少需要2组数据点才能绘制曲线")
    
    # 检查x值是否严格递增（插值要求）
    if not all(x_list[i] < x_list[i+1] for i in range(len(x_list)-1)):
        # 如果不是递增的，先排序
        sorted_pairs = sorted(zip(x_list, y_list), key=lambda p: p[0])
        x_list, y_list = zip(*sorted_pairs)
        x_list = list(x_list)
        y_list = list(y_list)
    
    return x_list, y_list


def smooth_curve(x_list: list[float], y_list: list[float], method: str = 'cubic', num_points: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """
    平滑曲线处理
    
    Args:
        x_list: 原始x坐标列表
        y_list: 原始y坐标列表
        method: 插值方法 ('linear', 'cubic', 'quadratic', 'akima')
        num_points: 生成的平滑曲线上的点数
    
    Returns:
        smooth_x, smooth_y: 平滑后的x和y坐标数组
    """
    if len(x_list) < 2:
        raise ValueError("数据点不足")
    
    # 生成等距的x坐标
    smooth_x = np.linspace(min(x_list), max(x_list), num_points)
    
    try:
        if method == 'linear':
            interp_func = interpolate.interp1d(x_list, y_list, kind='linear')
        elif method == 'quadratic':
            interp_func = interpolate.interp1d(x_list, y_list, kind='quadratic')
        elif method == 'cubic':
            interp_func = interpolate.interp1d(x_list, y_list, kind='cubic')
        elif method == 'akima':
            interp_func = interpolate.Akima1DInterpolator(x_list, y_list)
        else:
            raise ValueError(f"不支持的插值方法: {method}")
        
        smooth_y = interp_func(smooth_x)
    except Exception as e:
        # 如果高级插值失败，回退到线性插值
        interp_func = interpolate.interp1d(x_list, y_list, kind='linear')
        smooth_y = interp_func(smooth_x)
    
    return smooth_x, smooth_y


def calculate_statistics(y_list: list[float]) -> dict:
    """
    计算数据的基本统计信息
    
    Args:
        y_list: y坐标列表
    
    Returns:
        包含统计信息的字典
    """
    return {
        '最小值': min(y_list),
        '最大值': max(y_list),
        '平均值': sum(y_list) / len(y_list),
        '数据点数': len(y_list)
    }