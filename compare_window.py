# compare_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

class CompareWindow(QWidget):
    def __init__(self, std_wave, rec_wave, sample_rate):
        super().__init__()
        self.setWindowTitle("录音与标准对比结果")
        self.resize(1000, 400)

        layout = QVBoxLayout(self)

        # 显示对比信息
        label = QLabel("标准 vs 录音波形对比")
        layout.addWidget(label)

        # 添加波形图（叠加显示）
        fig = Figure(figsize=(10, 3))
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        t_std = np.arange(len(std_wave)) / sample_rate
        t_rec = np.arange(len(rec_wave)) / sample_rate

        ax.plot(t_std, std_wave, label='标准发音', alpha=0.8)
        ax.plot(t_rec, rec_wave, label='你的发音', alpha=0.6)
        ax.set_title("波形叠加对比")
        ax.set_xlabel("时间（秒）")
        ax.set_ylabel("幅度")
        ax.legend()
        fig.tight_layout()

        layout.addWidget(canvas)
