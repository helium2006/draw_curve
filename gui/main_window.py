#!/usr/bin/env python3
"""
main_window.py
主窗口类，实现用户界面和绘图功能
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel, QMessageBox, QComboBox, QFileDialog,
    QGroupBox, QFormLayout, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from utils.data_processor import parse_input_data, smooth_curve, calculate_statistics


class MainWindow(QMainWindow):
    """
    主窗口类，实现曲线绘制和导出功能
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.x_data = []
        self.y_data = []
        self.smooth_x = None
        self.smooth_y = None
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 设置窗口标题和大小
        self.setWindowTitle('光滑曲线图绘制工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧面板 - 数据输入
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 数据输入框
        data_group = QGroupBox('数据输入')
        data_layout = QVBoxLayout(data_group)
        
        self.data_input = QTextEdit()
        self.data_input.setPlaceholderText('请输入(x,y)数据点，每行一组，用空格、逗号或制表符分隔\n例如：\n1.0 2.0\n2.0 4.0\n3.0 3.5\n4.0 5.0')
        data_layout.addWidget(self.data_input)
        
        # 预设数据按钮
        preset_btn = QPushButton('加载示例数据')
        preset_btn.clicked.connect(self.load_preset_data)
        data_layout.addWidget(preset_btn)
        
        # 插值方法选择和坐标轴设置
        method_group = QGroupBox('插值和坐标轴设置')
        method_layout = QFormLayout(method_group)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(['cubic', 'quadratic', 'linear', 'akima'])
        self.method_combo.setCurrentText('cubic')
        method_layout.addRow('插值方法:', self.method_combo)
        
        # 添加坐标轴名称输入框
        self.x_label_input = QTextEdit()
        self.x_label_input.setPlaceholderText('X轴名称')
        self.x_label_input.setMaximumHeight(40)
        self.x_label_input.setText('X 坐标')
        method_layout.addRow('X轴名称:', self.x_label_input)
        
        self.y_label_input = QTextEdit()
        self.y_label_input.setPlaceholderText('Y轴名称')
        self.y_label_input.setMaximumHeight(40)
        self.y_label_input.setText('Y 坐标')
        method_layout.addRow('Y轴名称:', self.y_label_input)
        
        # 绘图和导出按钮
        btn_layout = QHBoxLayout()
        self.plot_btn = QPushButton('绘制曲线')
        self.plot_btn.clicked.connect(self.plot_curve)
        self.export_btn = QPushButton('导出图片')
        self.export_btn.clicked.connect(self.export_image)
        self.export_btn.setEnabled(False)
        
        btn_layout.addWidget(self.plot_btn)
        btn_layout.addWidget(self.export_btn)
        
        # 统计信息显示
        self.stats_label = QLabel('统计信息将在这里显示')
        self.stats_label.setWordWrap(True)
        
        # 添加到左侧布局
        left_layout.addWidget(data_group)
        left_layout.addWidget(method_group)
        left_layout.addLayout(btn_layout)
        left_layout.addWidget(self.stats_label)
        
        # 右侧面板 - 绘图区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 创建Matplotlib图形
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, right_panel)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        # 添加面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])  # 设置初始大小比例
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
    
    def load_preset_data(self):
        """
        加载预设的示例数据
        """
        preset_data = '''
# 示例数据：正弦曲线采样点
0.0 0.0
1.0 0.841
2.0 0.909
3.0 0.141
4.0 -0.757
5.0 -0.959
6.0 -0.279
7.0 0.657
8.0 0.989
9.0 0.412
10.0 -0.544
        '''
        self.data_input.setText(preset_data)
    
    def plot_curve(self):
        """
        绘制曲线
        """
        try:
            # 获取输入数据
            input_text = self.data_input.toPlainText()
            if not input_text.strip():
                QMessageBox.warning(self, '警告', '请输入数据')
                return
            
            # 解析数据
            self.x_data, self.y_data = parse_input_data(input_text)
            
            # 计算统计信息
            stats = calculate_statistics(self.y_data)
            stats_text = '统计信息:\n'
            for key, value in stats.items():
                if isinstance(value, float):
                    stats_text += f'{key}: {value:.6f}\n'
                else:
                    stats_text += f'{key}: {value}\n'
            self.stats_label.setText(stats_text)
            
            # 获取插值方法
            method = self.method_combo.currentText()
            
            # 生成平滑曲线
            self.smooth_x, self.smooth_y = smooth_curve(
                self.x_data, self.y_data, method=method, num_points=1000
            )
            
            # 绘制图形
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # 绘制原始数据点
            ax.scatter(self.x_data, self.y_data, color='red', label='原始数据点')
            
            # 绘制平滑曲线
            ax.plot(self.smooth_x, self.smooth_y, color='blue', linewidth=2, label=f'{method}插值曲线')
            
            # 获取用户自定义的坐标轴名称
            x_label = self.x_label_input.toPlainText().strip() or 'X 坐标'
            y_label = self.y_label_input.toPlainText().strip() or 'Y 坐标'
            
            # 设置图形属性
            ax.set_title('光滑曲线图')
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()
            
            # 调整布局
            self.figure.tight_layout()
            
            # 更新画布
            self.canvas.draw()
            
            # 启用导出按钮
            self.export_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'绘制失败：\n{str(e)}')
    
    def export_image(self):
        """
        导出图片
        """
        if self.smooth_x is None or self.smooth_y is None:
            QMessageBox.warning(self, '警告', '请先绘制曲线')
            return
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出图片', '', 'PNG文件 (*.png);;JPEG文件 (*.jpg);;SVG文件 (*.svg);;PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
        
        try:
            # 保存图片
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, '成功', f'图片已成功导出到:\n{file_path}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败：\n{str(e)}')


def main():
    """
    应用程序入口
    """
    # 确保中文显示正常
    import matplotlib
    matplotlib.use('Qt5Agg')
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()