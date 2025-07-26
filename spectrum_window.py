# spectrum_window.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy.io import wavfile
import numpy as np
import os


class SpectrumCanvas(FigureCanvasQTAgg):
    def __init__(self, title, data, sample_rate):
        self.fig = Figure(figsize=(8, 3))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(title)
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Magnitude (dB)")
        self.plot_spectrum(data, sample_rate)
        self.fig.tight_layout()

    def plot_spectrum(self, data, sample_rate):
        data = data.astype(np.float32)
        if np.max(np.abs(data)) > 0:
            data /= np.max(np.abs(data))

        window = np.hanning(len(data))
        data_windowed = data * window

        fft_data = np.fft.rfft(data_windowed)
        magnitude = 20 * np.log10(np.abs(fft_data) + 1e-10)
        freq = np.fft.rfftfreq(len(data), d=1.0 / sample_rate)

        self.ax.plot(freq, magnitude)
        self.ax.set_xlim(0, 5000)  # 0–5kHz voice range


class SpectrumWindow(QWidget):
    def __init__(self, sample_rate):
        super().__init__()
        self.setWindowTitle("Spectrogram of Standard and Recorded Audio")
        self.resize(1000, 600)

        layout = QVBoxLayout(self)

        # Load standard audio
        if os.path.exists("std_audio.wav"):
            sr1, std_data = wavfile.read("std_audio.wav")
            if std_data.ndim > 1:
                std_data = std_data[:, 0]
            std_canvas = SpectrumCanvas("Standard Audio Spectrum", std_data, sr1)
            layout.addWidget(std_canvas)
        else:
            layout.addWidget(QLabel("Standard audio file (std_audio.wav) not found."))

        # Load recorded audio
        if os.path.exists("recorded.wav"):
            sr2, rec_data = wavfile.read("recorded.wav")
            if rec_data.ndim > 1:
                rec_data = rec_data[:, 0]
            rec_canvas = SpectrumCanvas("Recorded Audio Spectrum", rec_data, sr2)
            layout.addWidget(rec_canvas)
        else:
            layout.addWidget(QLabel("Recorded audio file (recorded.wav) not found."))

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
