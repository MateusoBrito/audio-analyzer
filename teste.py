# ============================================================
# Script de Análise de Áudio para Caracterização de Instrumento
# ============================================================
# Autor: Coloca o nome de todas e todos aqui, por favor.
# Objetivo: caracterizar instrumentos em termos de
# parâmetros temporais, espectrais e tempo-frequência.
# ============================================================

# -----------------------------
# (1) Importação de bibliotecas
# -----------------------------
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

# -----------------------------
# (2) Carregar o arquivo de áudio
# -----------------------------
# Substitua 'meu_audio.wav' pelo caminho do seu arquivo
y, sr = librosa.load("file_example_WAV_1MG.wav", sr=None)

# -----------------------------
# (3) Análise no domínio do tempo
# -----------------------------
# 3.1 - Cálculo do envelope RMS
frame_length = 2048
hop_length = 512
rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

# 3.2 - Cálculo do fator de crista (Crest Factor)
peak = np.max(np.abs(y))
rms_global = np.sqrt(np.mean(y**2))
crest_factor = peak / rms_global

print(f"Crest Factor: {crest_factor:.2f}")

# -----------------------------
# (4) Análise espectral (frequência)
# -----------------------------
# 4.1 - Espectro médio (FFT)
fft = np.fft.fft(y)
magnitude = np.abs(fft)[:len(fft)//2]
freqs = np.fft.fftfreq(len(fft), 1/sr)[:len(fft)//2]

# 4.2 - Centróide espectral
centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

# 4.3 - Roll-off espectral
rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]

# -----------------------------
# (5) Análise tempo-frequência
# -----------------------------
# 5.1 - Espectrograma STFT
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop_length))
S_db = librosa.amplitude_to_db(S, ref=np.max)

# -----------------------------
# (6) Extração de parâmetros adicionais
# -----------------------------
# 6.1 - Pitch tracking (f0)
f0, voiced_flag, voiced_probs = librosa.pyin(y,
                                             fmin=librosa.note_to_hz('C2'),
                                             fmax=librosa.note_to_hz('C7'))

# 6.2 - Envelope de amplitude via transformada de Hilbert
analytic_signal = hilbert(y)
amplitude_envelope = np.abs(analytic_signal)

# -----------------------------
# (7) Visualizações
# -----------------------------
plt.figure(figsize=(14, 10))

# 7.1 - Onda + envelope RMS
plt.subplot(3,1,1)
librosa.display.waveshow(y, sr=sr, alpha=0.6)
plt.plot(librosa.times_like(rms, sr=sr, hop_length=hop_length),
         rms, color='r', label='RMS')
plt.title("Forma de onda + Envelope RMS")
plt.legend()

# 7.2 - Espectrograma
plt.subplot(3,1,2)
librosa.display.specshow(S_db, sr=sr, hop_length=hop_length,
                         x_axis='time', y_axis='hz', cmap='magma')
plt.colorbar(format="%+2.f dB")
plt.title("Espectrograma (STFT)")

# 7.3 - Centróide espectral ao longo do tempo
plt.subplot(3,1,3)
plt.semilogy(librosa.times_like(centroid, sr=sr, hop_length=hop_length),
             centroid.T, label='Centróide espectral')
plt.ylabel('Hz')
plt.xlabel('Tempo (s)')
plt.title("Centróide espectral")
plt.legend()

plt.tight_layout()
plt.show()

# -----------------------------
# (8) Saída resumida
# -----------------------------
print("Resumo da análise:")
print(f"- Taxa de amostragem: {sr} Hz")
print(f"- Duração: {len(y)/sr:.2f} s")
print(f"- Crest Factor: {crest_factor:.2f}")
print(f"- Centróide espectral médio: {np.mean(centroid):.2f} Hz")
print(f"- Roll-off espectral médio: {np.mean(rolloff):.2f} Hz")
print(f"- Fundamental média (f0): {np.nanmean(f0):.2f} Hz")