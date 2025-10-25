#!/usr/bin/env python3
"""
main.py
绘制光滑曲线图程序的主入口
"""

import sys


def main():
    """
    主程序入口
    """
    try:
        # 导入主窗口类
        from gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        import matplotlib
        import matplotlib.pyplot as plt
        
        # 设置 matplotlib 后端
        matplotlib.use('Qt5Agg')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"导入错误：缺少必要的库，请安装依赖：{e}")
        print("推荐使用以下命令安装依赖：")
        print("pip install PyQt6 matplotlib numpy scipy")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错：{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()