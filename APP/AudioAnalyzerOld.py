import librosa
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import hilbert
from numpy.fft import rfft, rfftfreq


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
        #times = librosa.times_like(y, sr=sr)
        if y.ndim > 1:
            y = y[:, 0]
        
        target_points = 8000 
        if len(y) > target_points:
            step = len(y) // target_points
            y_reduced = y[::step]
            times = np.linspace(0, len(y) / sr, num=len(y_reduced))
            return times, y_reduced
        
        # Se for curto, retorna tudo
        times = np.linspace(0, len(y) / sr, num=len(y))
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

        #S = librosa.stft(y)
        #S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

        n_fft = 2048
        hop_length = 1024 
        
        S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
        
        return S_db
    
    def get_hilbert_data(self, y): 
        #if y.ndim > 1:
        #    y = y[:, 0]

        #analytic_signal = hilbert(y)
        #amplitude_envelope = np.abs(analytic_signal)
        #samples = np.arange(len(amplitude_envelope))
        #return samples, amplitude_envelope

        target_points = 10000 
        if len(y) > target_points:
            step = len(y) // target_points
            y_reduced = y[::step]
        else:
            y_reduced = y
            step = 1
        
        analytic_signal = hilbert(y_reduced)
        amplitude_envelope = np.abs(analytic_signal)
        samples = np.arange(len(amplitude_envelope)) * step
        return samples, amplitude_envelope

    def get_advanced_metrics(self, y, sr):
        """
        Calcula métricas avançadas (Crest Factor, Centróide, F0, etc).
        Retorna um dicionário com os valores formatados.
        """
        # Garante mono para análise de características globais
        if y.ndim > 1:
            y_mono = y[:, 0]
        else:
            y_mono = y

        # 1. Crest Factor
        peak = np.max(np.abs(y_mono))
        rms_global = np.sqrt(np.mean(y_mono**2))
        crest_factor = peak / (rms_global if rms_global > 0 else 1)

        # 2. Centróide Espectral (Média)
        centroid = librosa.feature.spectral_centroid(y=y_mono, sr=sr)[0]
        avg_centroid = np.mean(centroid)

        # 3. Roll-off Espectral (Média)
        rolloff = librosa.feature.spectral_rolloff(y=y_mono, sr=sr, roll_percent=0.85)[0]
        avg_rolloff = np.mean(rolloff)

        # 4. F0 (Fundamental) - Usando PYIN (pode ser pesado, mas é preciso)
        # Ajustamos fmin/fmax para uma faixa razoável de instrumentos
        f0, _, _ = librosa.pyin(
            y_mono, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7'),
            sr=sr
        )
        avg_f0 = np.nanmean(f0) if np.any(~np.isnan(f0)) else 0.0

        return {
            "sr": sr,
            "duration": len(y_mono)/sr,
            "crest_factor": crest_factor,
            "centroid": avg_centroid,
            "rolloff": avg_rolloff,
            "f0": avg_f0
        }