import sys
import numpy as np
from scipy.io import wavfile
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from audio_processing import AudioProcessor, load_standard_waveform
from compare import compare_waveforms
from settings_window import SettingsDialog
from spectrum_window import SpectrumWindow
import os

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, title, max_len_samples, sample_rate):
        self.fig = Figure(figsize=(10, 3))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.sample_rate = sample_rate
        self.max_len = max_len_samples
        self.ax.set_title(title)
        self.ax.set_xlim(0, max_len_samples / sample_rate)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlabel("时间 (秒)")
        self.ax.set_ylabel("幅度")
        self.line, = self.ax.plot(np.zeros(max_len_samples), lw=0.7)
        self.fig.tight_layout()

    def update_waveform(self, y):
        y = np.asarray(y)
        if len(y) != self.max_len:
            if len(y) > self.max_len:
                y = y[-self.max_len:]
            else:
                y = np.pad(y, (self.max_len - len(y), 0), mode='constant')
        t = np.arange(len(y)) / self.sample_rate
        self.line.set_xdata(t)
        self.line.set_ydata(y)
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("标准波形 & 实时录音波形对比 - 模块化版本")
        self.sample_rate = 44100
        self.duration_sec = 5
        self.max_len_samples = self.sample_rate * self.duration_sec

        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)

        # 输入和按钮区域
        input_layout = QHBoxLayout()
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("输入英文句子，例如：This is a test")
        input_layout.addWidget(self.input_text)

        self.generate_btn = QPushButton("生成标准波形（英式发音）")
        self.generate_btn.clicked.connect(self.generate_std_waveform)
        input_layout.addWidget(self.generate_btn)

        self.setting_btn = QPushButton("设置")
        self.setting_btn.clicked.connect(self.show_settings_dialog)
        input_layout.addWidget(self.setting_btn)

        self.spectrum_btn = QPushButton("查看频谱图")
        self.spectrum_btn.clicked.connect(self.open_spectrum_window)
        input_layout.addWidget(self.spectrum_btn)

        self.layout.addLayout(input_layout)

        self.label_std = QLabel("标准读音波形（固定）")
        self.layout.addWidget(self.label_std)
        self.std_canvas = MplCanvas("标准读音", self.max_len_samples, self.sample_rate)
        self.layout.addWidget(self.std_canvas)

        self.label_live = QLabel("实时录音波形（点击按钮开始）")
        self.layout.addWidget(self.label_live)
        self.live_canvas = MplCanvas("实时录音", self.max_len_samples, self.sample_rate)
        self.layout.addWidget(self.live_canvas)

        # 录音和播放按钮
        button_layout = QHBoxLayout()
        self.btn_start = QPushButton("开始录音")
        self.btn_stop = QPushButton("结束录音")
        self.btn_play_std = QPushButton("播放标准读音")
        self.btn_play_recorded = QPushButton("播放录音")
        self.btn_compare = QPushButton("对比录音与标准")

        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_play_std)
        button_layout.addWidget(self.btn_play_recorded)
        button_layout.addWidget(self.btn_compare)
        self.layout.addLayout(button_layout)

        # 音频处理实例
        self.audio_processor = AudioProcessor(self.sample_rate, self.duration_sec)
        self.audio_processor.start_stream(self.audio_processor.audio_callback)

        # 计时器刷新实时波形
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_waveform)
        self.timer.start(50)

        # 绑定按钮事件
        self.btn_start.clicked.connect(self.start_recording)
        self.btn_stop.clicked.connect(self.stop_recording)
        self.btn_play_std.clicked.connect(self.play_std_audio)
        self.btn_play_recorded.clicked.connect(self.play_recorded_audio)
        self.btn_compare.clicked.connect(self.compare_recorded_with_std)

        # 初始加载标准波形和句子
        self.load_and_display_std_waveform()

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.duration_sec = dialog.duration_spin.value()
            self.max_len_samples = self.sample_rate * self.duration_sec
            self.audio_processor.duration_sec = self.duration_sec
            self.audio_processor.max_len_samples = self.max_len_samples
            # 更新波形画布
            self.std_canvas.setParent(None)
            self.live_canvas.setParent(None)
            self.std_canvas = MplCanvas("标准读音", self.max_len_samples, self.sample_rate)
            self.live_canvas = MplCanvas("实时录音", self.max_len_samples, self.sample_rate)
            self.layout.insertWidget(2, self.std_canvas)
            self.layout.insertWidget(4, self.live_canvas)
            self.load_and_display_std_waveform()

    def load_and_display_std_waveform(self):
        try:
            std_wave = load_standard_waveform("std_audio.wav", self.max_len_samples)
            self.std_canvas.update_waveform(std_wave)
            if os.path.exists("std_audio.txt"):
                with open("std_audio.txt", "r", encoding="utf-8") as f:
                    self.input_text.setText(f.read())
        except Exception as e:
            print(f"加载标准波形失败: {e}")

    def generate_std_waveform(self):
        text = self.input_text.text().strip()
        if not text:
            return
        self.audio_processor.generate_std_audio(text)
        # 保存文本
        with open("std_audio.txt", "w", encoding="utf-8") as f:
            f.write(text)
        self.load_and_display_std_waveform()

    def update_live_waveform(self):
        data = np.array(self.audio_processor.live_buffer)
        if len(data) == 0:
            return
        if np.max(np.abs(data)) > 0:
            data = data / np.max(np.abs(data))
        self.live_canvas.update_waveform(data)

    def start_recording(self):
        self.audio_processor.start_recording()
        print("录音开始...")

    def stop_recording(self):
        recorded_data = self.audio_processor.stop_recording()
        if recorded_data is not None:
            print("录音结束，文件已保存")
        else:
            print("没有录音数据")

    def play_std_audio(self):
        self.audio_processor.play_audio("std_audio.wav")

    def play_recorded_audio(self):
        self.audio_processor.play_audio("recorded.wav")

    def compare_recorded_with_std(self):
        if not os.path.exists("std_audio.wav"):
            print("标准音频不存在，请先生成")
            return
        if not os.path.exists("recorded.wav"):
            print("录音文件不存在，请先录音")
            return

        _, std_wave = wavfile.read("std_audio.wav")
        if std_wave.ndim > 1:
            std_wave = std_wave[:, 0]
        std_wave = std_wave.astype(np.float32)
        std_wave /= np.max(np.abs(std_wave))

        _, rec_wave = wavfile.read("recorded.wav")
        if rec_wave.ndim > 1:
            rec_wave = rec_wave[:, 0]
        rec_wave = rec_wave.astype(np.float32)
        rec_wave /= np.max(np.abs(rec_wave))

        dist = compare_waveforms(std_wave, rec_wave)
        print(f"DTW距离（越小越相似）: {dist:.4f}")

    def open_spectrum_window(self):
        self.spectrum_window = SpectrumWindow(self.sample_rate)
        self.spectrum_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())
