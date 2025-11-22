import librosa
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import hilbert

class AudioAnalyzer:
    """
    Responsável por todos os cálculos de análise de áudio.
    """
    def get_fft_data(self, y, sr, fi=20, fm=20000, fft_scale=1):
        if y.ndim == 1:
            y = np.column_stack((y, y))

        n = len(y)
        step = max(1, int(fft_scale))
        freq = fftfreq(n, 1/sr)[:n//2:step]

        L = np.abs(fft(y[:, 0]))[:n//2:step]
        R = np.abs(fft(y[:, 1]))[:n//2:step]

        mascara = (freq >= fi) & (freq <= fm)
        freq_filtrado = freq[mascara]
        
        L_max = np.max(L[mascara]) or 1
        R_max = np.max(R[mascara]) or 1

        L_norm = L[mascara] / L_max
        R_norm = R[mascara] / R_max

        return freq_filtrado, L_norm, R_norm

    def get_waveform_data(self, y, sr):
        times = librosa.times_like(y, sr=sr)
        if y.ndim > 1:
            y = y[:, 0]
        return times, y

    def get_rms_data(self, y, sr, frame_length=2048, hop_length=512):
        if y.ndim > 1:
            y = y[:, 0]

        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
        return times, rms

    def get_spectrogram_data(self, y, sr=None): 
        if y.ndim > 1:
            y = y[:, 0]

        S = librosa.stft(y)
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
        return S_db
    
    def get_hilbert_data(self, y): 
        if y.ndim > 1:
            y = y[:, 0]

        analytic_signal = hilbert(y)
        amplitude_envelope = np.abs(analytic_signal)
        samples = np.arange(len(amplitude_envelope))
        return samples, amplitude_envelope