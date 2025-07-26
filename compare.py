from dtw import dtw
import numpy as np

def compare_waveforms(wave1, wave2, max_len=30000):
    max_len = min(len(wave1), len(wave2), max_len)
    w1 = wave1[:max_len]
    w2 = wave2[:max_len]

    # 计算DTW距离，返回一个DTW对象
    alignment = dtw(w1, w2)

    # 返回距离（越小越相似）
    return alignment.distance
