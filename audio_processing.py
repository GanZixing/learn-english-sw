import os
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import pyttsx3
from collections import deque

class AudioProcessor:
    def __init__(self, sample_rate=44100, duration_sec=5):
        self.sample_rate = sample_rate
        self.duration_sec = duration_sec
        self.max_len_samples = sample_rate * duration_sec
        self.live_buffer = deque(maxlen=self.max_len_samples)
        self.recording = []
        self.is_recording = False
        self.stream = None

    def start_stream(self, callback):
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=callback
        )
        self.stream.start()

    def stop_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def start_recording(self):
        self.recording = []
        self.is_recording = True
        self.live_buffer.clear()

    def stop_recording(self):
        self.is_recording = False
        if not self.recording:
            return None
        all_data = np.concatenate(self.recording, axis=0)
        all_data = all_data[:, 0]
        all_data = np.clip(all_data, -1.0, 1.0)
        all_data_int16 = (all_data * 32767).astype(np.int16)
        wavfile.write("recorded.wav", self.sample_rate, all_data_int16)
        return all_data

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.live_buffer.extend(indata[:, 0])
            self.recording.append(indata.copy())

    def play_audio(self, filename):
        if not os.path.exists(filename):
            print(f"文件 {filename} 不存在！")
            return
        sample_rate, data = wavfile.read(filename)
        sd.play(data, samplerate=sample_rate)

    def generate_std_audio(self, text):
        if not text.strip():
            return
        engine = pyttsx3.init()
        for voice in engine.getProperty('voices'):
            if 'english' in voice.name.lower() and ('gb' in voice.id.lower() or 'bri' in voice.name.lower()):
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 160)
        engine.save_to_file(text, "std_audio.wav")
        engine.runAndWait()

def load_standard_waveform(filename, max_len_samples):
    from scipy.io import wavfile
    import numpy as np

    sample_rate, data = wavfile.read(filename)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(np.float32)
    data /= np.max(np.abs(data))
    if len(data) > max_len_samples:
        factor = len(data) / max_len_samples
        compressed = []
        for i in range(max_len_samples):
            start = int(i * factor)
            end = int((i + 1) * factor)
            compressed.append(np.max(np.abs(data[start:end])))
        data = np.array(compressed)
    else:
        data = np.pad(data, (0, max_len_samples - len(data)), mode='constant')
    return data
