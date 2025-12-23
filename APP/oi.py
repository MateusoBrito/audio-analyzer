'''
Funções para análise na frequência de sinais de áudio com limites de faixa.
'''
# Importações no formato solicitado
from scipy.io.wavfile import read
from scipy.signal import stft, spectrogram, get_window
from numpy.fft import rfft, rfftfreq
from numpy import ( abs, argmax, std, clip, log10, zeros, where, maximum, 
                   minimum, meshgrid, angle, unwrap, diff, pi, arange)
from matplotlib.pyplot import (figure, plot, pcolormesh, colorbar, title, 
                               xlabel, ylabel, grid, legend, close)
from scipy.signal import hilbert 
from matplotlib.pyplot import show

def carregar_audio(caminho_arquivo):
    """
    Lê um arquivo WAV e retorna (fs, x_float).
    Converte para float entre [-1, 1] se estiver em inteiro.
    """
    fs, x = read(caminho_arquivo)
    if x.dtype.kind in ('i', 'u'):
        max_val = 2 ** (8 * x.dtype.itemsize - 1)
        x = x.astype('float32') / max_val
    else:
        x = x.astype('float32')
    if len(x.shape) == 2 and x.shape[1] > 1:
        x = (x[:, 0] + x[:, 1]) / 2.0
    return fs, x

def calcular_fft_basica(x, fs, fmin=None, fmax=None):
    """
    Calcula FFT de magnitude unilateral (rfft).
    Retorna (f, Xmag), onde f são frequências em Hz e Xmag magnitudes.
    Permite limitar a faixa de frequências com fmin e fmax.
    """
    N = len(x)
    X = rfft(x)
    f = rfftfreq(N, d=1.0/fs)
    Xmag = abs(X)
    if fmin is not None or fmax is not None:
        mask = (f >= (fmin if fmin else f[0])) & (f <= (fmax if fmax else f[-1]))
        f = f[mask]
        Xmag = Xmag[mask]
    return f, Xmag

def calcular_stft(x, fs, janela='hann', nperseg=2048, noverlap=1024, fmin=None, fmax=None):
    """
    Calcula STFT usando scipy.signal.stft.
    Retorna (t, f, Zxx) onde Zxx é complexo (tempo x frequência).
    Permite limitar a faixa de frequências com fmin e fmax.
    """
    win = get_window(janela, nperseg)
    f, t, Zxx = stft(x, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, boundary=None)
    if fmin is not None or fmax is not None:
        mask = (f >= (fmin if fmin else f[0])) & (f <= (fmax if fmax else f[-1]))
        f = f[mask]
        Zxx = Zxx[mask, :]
    return t, f, Zxx

def calcular_espectrograma(x, fs, janela='hann', nperseg=2048, noverlap=1024, fmin=None, fmax=None):
    """
    Calcula espectrograma (potência) usando scipy.signal.spectrogram.
    Retorna (t, f, Sxx).
    Permite limitar a faixa de frequências com fmin e fmax.
    """
    win = get_window(janela, nperseg)
    f, t, Sxx = spectrogram(x, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, mode='psd')
    if fmin is not None or fmax is not None:
        mask = (f >= (fmin if fmin else f[0])) & (f <= (fmax if fmax else f[-1]))
        f = f[mask]
        Sxx = Sxx[mask, :]
    return t, f, Sxx

def estimar_fundamental_por_pico_espectral(Zxx, f, faixa=(50.0, 2000.0)):
    """
    Estima a frequência fundamental em cada frame de STFT procurando o pico dominante
    dentro de uma faixa plausível.
    """
    mag = abs(Zxx)
    fmin, fmax = faixa
    idx_validos = where((f >= fmin) & (f <= fmax))[0]
    f0 = zeros(mag.shape[1], dtype='float32')
    for k in range(mag.shape[1]):
        col = mag[idx_validos, k]
        if col.size == 0:
            f0[k] = 0.0
            continue
        ipeak = argmax(col)
        f0[k] = f[idx_validos[ipeak]]
    return f0

def rastrear_harmonicos(Zxx, f, f0_series, nharm=6, largura_relativa=0.015):
    """
    Rastreia até nharm harmônicos ao longo do tempo a partir de f0_series.
    """
    mag = abs(Zxx)
    T = mag.shape[1]
    Hfreqs = []
    for h in range(1, nharm+1):
        hf = zeros(T, dtype='float32')
        Hfreqs.append(hf)

    for k in range(T):
        f0k = f0_series[k]
        if f0k <= 0.0:
            continue
        for h in range(1, nharm+1):
            alvo = h * f0k
            largura = max(largura_relativa * alvo, 5.0)
            fmin = maximum(alvo - largura, f[0])
            fmax = minimum(alvo + largura, f[-1])
            idx = where((f >= fmin) & (f <= fmax))[0]
            if idx.size == 0:
                Hfreqs[h-1][k] = 0.0
                continue
            ipeak_local = idx[argmax(mag[idx, k])]
            Hfreqs[h-1][k] = f[ipeak_local]
    return Hfreqs

def calcular_desvio_padrao_desvio(Hfreqs, f0_target):
    """
    Calcula desvio-padrão dos desvios de frequência (em cents) para cada harmônico.
    """
    cents_std = []
    cents_series = []
    for h, hf_series in enumerate(Hfreqs, start=1):
        alvo = h * f0_target
        fmed = clip(hf_series, 1e-6, None)
        cents = 1200.0 * (log10(fmed / alvo) / log10(2.0))
        cents = where(hf_series <= 0.0, 0.0, cents)
        validos = where(hf_series > 0.0)[0]
        if validos.size > 0:
            std_cents = std(cents[validos])
        else:
            std_cents = 0.0
        cents_std.append(std_cents)
        cents_series.append(cents)
    return cents_std, cents_series

close('all')

fs, sinal = carregar_audio("../audios/21170__reinsamba__pandeiro-7.wav")

fmin = 20
fmax = 7500

# 1. Calcula a FFT Básica
F, Xmag = calcular_fft_basica(sinal, fs, fmin=fmin, fmax=fmax)
figure(1)
plot(F, Xmag)
title("Espectro de Frequências Total")
ylabel("Magnitude")
xlabel("Frequência (Hz)")
grid('on')

# 2. Calcula a STFT (Mudei o nome de t para t_stft)
t_stft, F_stft, Zxx = calcular_stft(sinal, fs, janela='hann', nperseg=2048, noverlap=1024, fmin=fmin, fmax=fmax)

Zxx_mag = 20 * log10(abs(Zxx) + 1e-10)

T_stft, Fgrid = meshgrid(t_stft, F_stft)

# Plot 3D
fig = figure(2)
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(T_stft, Fgrid, Zxx_mag, cmap='viridis') # Usa T_stft aqui
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Frequência (Hz)")
ax.set_zlabel("Magnitude (dB)")
ax.set_title("Espectro de Frequências de Curto Prazo")

# 3. Calcula o Espectrograma (Mudei o nome de t para t_spec)
t_spec, f_spec, Sxx = calcular_espectrograma(sinal, fs, janela='hann', nperseg=2048, noverlap=1024, fmin=fmin, fmax=fmax)
Sxx_db = 10 * log10(Sxx + 1e-10)

figure(3)
pcolormesh(t_spec, f_spec, Sxx_db, shading='gouraud') # Usa t_spec aqui
colorbar(label='Potência (dB)')
title('Espectrograma - Tempo x Frequência')
xlabel('Tempo (s)')
ylabel('Frequência (Hz)')

# 4. Estima a frequência fundamental (Baseado no Zxx da STFT)
f0_series = estimar_fundamental_por_pico_espectral(Zxx, F_stft, faixa=(fmin, fmax))

# Plotar a variação da afinação (MUITO IMPORTANTE: Usar t_stft, pois f0 vem de Zxx)
figure(4)
plot(t_stft, f0_series, color='blue') # Correção aqui: t_stft em vez de t
title("Variação da Afinação")
xlabel("Tempo (s)")
ylabel("Frequência Fundamental (Hz)")
grid(True)

# ... (O resto do código com Hilbert permanece igual, pois cria seu próprio vetor 'tempo') ...
# --- Análise com Hilbert ---
sinal_analitico = hilbert(sinal)
fase_instantanea = unwrap(angle(sinal_analitico))
freq_instantanea = diff(fase_instantanea) / (2*pi) * fs

tempo = arange(len(sinal))/fs

# Plotar frequência instantânea
figure(5)
plot(tempo[1:], freq_instantanea, color='green')
title("Pitch estimado via Transformada de Hilbert")
xlabel("Tempo (s)")
ylabel("Frequência Instantânea (Hz)")
grid(True)

# --- Envoltória ---
envoltoria = abs(sinal_analitico)

figure(6)
plot(tempo, envoltoria, 'r--', label="Envoltória")
title("Sinal e sua Envoltória")
xlabel("Tempo (s)")
ylabel("Amplitude")
legend()
grid(True)

show()