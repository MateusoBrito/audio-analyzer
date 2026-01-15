import numpy as np
from numpy.fft import rfft, rfftfreq
from scipy.signal import stft, spectrogram, get_window, hilbert

class AudioAnalyzer:
    """
    Responsável por todos os cálculos de análise de áudio.
    """
    def calcular_fft_basica(self, x, fs, fmin=None, fmax=None):
        """
        Calcula FFT de magnitude unilateral (rfft).
        Retorna (f, Xmag), onde f são frequências em Hz e Xmag magnitudes.
        Permite limitar a faixa de frequências com fmin e fmax.
        """
        N = len(x)
        X = rfft(x)
        f = rfftfreq(N, d=1.0/fs)
        Xmag = np.abs(X)
        
        if fmin is not None or fmax is not None:
            mask = (f >= (fmin if fmin else f[0])) & (f <= (fmax if fmax else f[-1]))
            f = f[mask]
            Xmag = Xmag[mask]
        return f, Xmag

    def calcular_stft(self, x, fs, janela='hann', nperseg=2048, noverlap=1024, fmin=None, fmax=None):
        """
        Calcula STFT usando scipy.signal.stft.
        Retorna (t, f, Zxx) onde Zxx é complexo (tempo x frequência).
        Permite limitar a faixa de frequências com fmin e fmax.
        """
        win = get_window(janela, nperseg)
        # boundary=None é importante para bater com o código do cliente
        f, t, Zxx = stft(x, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, boundary=None)
        
        if fmin is not None or fmax is not None:
            mask = (f >= (fmin if fmin else f[0])) & (f <= (fmax if fmax else f[-1]))
            f = f[mask]
            Zxx = Zxx[mask, :]
        return t, f, Zxx

    def get_sfft_3d_data(self, x, fs, fmin=20, fmax=20000):
        """
        Prepara os dados (X, Y, Z) para o plot de superfície 3D.
        """
        # 1. Calcula STFT
        t, f, Zxx = self.calcular_stft(x, fs, fmin=fmin, fmax=fmax)
        
        # 2. Converte para dB (Magnitude)
        Zxx_mag = 20 * np.log10(np.abs(Zxx) + 1e-10)
        
        # 3. Cria a grade (Meshgrid) necessária para superfícies 3D
        T, Fgrid = np.meshgrid(t, f)
        
        return T, Fgrid, Zxx_mag
    
    def calcular_espectrograma(self, x, fs, fmin=None, fmax=None):
        """
        Calcula espectrograma (potência) usando scipy.signal.spectrogram.
        Retorna (t, f, Sxx).
        Permite limitar a faixa de frequências com fmin e fmax.
        """
        janela = 'hann'
        nperseg = 2048
        noverlap = 1024
        
        win = get_window(janela, nperseg)
        f, t, Sxx = spectrogram(x, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, mode='psd')
        
        if fmin is not None or fmax is not None:
            mask = (f >= (fmin if fmin else f[0])) & (f <= (fmax if fmax else f[-1]))
            f = f[mask]
            Sxx = Sxx[mask, :]
            
        # Converte para dB aqui para facilitar o plot
        Sxx_db = 10 * np.log10(Sxx + 1e-10)
        return t, f, Sxx_db

    def estimar_fundamental_por_pico_espectral(self, Zxx, f, faixa):
        """
        Estima a frequência fundamental em cada frame de STFT procurando o pico dominante
        dentro de uma faixa plausível.
        """
        mag = np.abs(Zxx)
        fmin, fmax = faixa
        idx_validos = np.where((f >= fmin) & (f <= fmax))[0]
        f0 = np.zeros(mag.shape[1], dtype='float32')
        
        if len(idx_validos) == 0:
            return f0

        for k in range(mag.shape[1]):
            col = mag[idx_validos, k]
            if col.size == 0:
                f0[k] = 0.0
                continue
            ipeak = np.argmax(col)
            f0[k] = f[idx_validos[ipeak]]
        return f0
    
    def get_waveform_data(self, x, fs):
        """Retorna tempo e amplitude reduzidos para plotagem rápida."""
        target_points = 8000
        if len(x) > target_points:
            step = len(x) // target_points
            y_reduced = x[::step]
            times = np.linspace(0, len(x) / fs, num=len(y_reduced))
            return times, y_reduced
        
        times = np.linspace(0, len(x) / fs, num=len(x))
        return times, x
    
    def get_rms_data(self, x, fs):
        # Implementação simples de RMS deslizante (Numpy puro)
        frame_len = 2048
        hop = 1024
        x_sq = x**2
        window = np.ones(frame_len) / frame_len
        rms = np.sqrt(np.convolve(x_sq, window, mode='valid')[::hop])
        t = np.linspace(0, len(x)/fs, len(rms))
        return t, rms
    
    def get_metrics(self, x, fs, fmin=20, fmax=20000):
        # 1. Calcula STFT básica para métricas
        t, f, Zxx = self.calcular_stft(x, fs, fmin=fmin, fmax=fmax)
        
        # 2. Estima F0 usando a função do cliente
        f0_series = self.estimar_fundamental_por_pico_espectral(Zxx, f, faixa=(fmin, fmax))
        # Remove zeros para média
        valid_f0 = f0_series[f0_series > 0]
        avg_f0 = np.mean(valid_f0) if len(valid_f0) > 0 else 0.0

        # 3. Métricas globais (Crest Factor)
        peak = np.max(np.abs(x))
        rms = np.sqrt(np.mean(x**2))
        crest = peak / (rms + 1e-9)

        # 4. Centróide (Simplificado na faixa)
        mag = np.abs(Zxx)
        if mag.sum() > 0:
            freqs_matrix = np.tile(f.reshape(-1, 1), (1, mag.shape[1]))
            centroid = np.sum(freqs_matrix * mag) / np.sum(mag)
        else:
            centroid = 0.0

        return {
            "sr": fs,
            "duration": len(x)/fs,
            "crest_factor": crest,
            "centroid": centroid,
            "rolloff": 0.0, # Implementar se necessário com lógica similar
            "f0": avg_f0
        }
    
    def get_pitch_data(self, x, fs, fmin=20, fmax=20000):
        """
        Retorna (tempo, f0_series) para plotagem.
        """
        # 1. Reutiliza a STFT otimizada
        t, f, Zxx = self.calcular_stft(x, fs, fmin=fmin, fmax=fmax)
        
        # 2. Estima a fundamental (Lógica do cliente)
        f0_series = self.estimar_fundamental_por_pico_espectral(Zxx, f, faixa=(fmin, fmax))
        
        return t, f0_series

    def get_hilbert_envelope(self, x, fs):
        """
        Calcula a Envoltória (Lógica para o Gráfico Vermelho).
        """
        # Downsampling para não travar a interface (opcional, mas recomendado)
        target_points = 8000
        if len(x) > target_points:
            step = len(x) // target_points
            x_reduced = x[::step]
            t_reduced = np.linspace(0, len(x)/fs, len(x_reduced))
        else:
            x_reduced = x
            t_reduced = np.linspace(0, len(x)/fs, len(x))
            
        sinal_analitico = hilbert(x_reduced)
        envoltoria = np.abs(sinal_analitico)
        return t_reduced, envoltoria

    def get_instantaneous_frequency(self, x, fs):
        """
        Calcula a Frequência Instantânea (Lógica para o Gráfico Verde).
        Matemática: diff(unwrap(angle(hilbert(x))))
        """
        # Downsampling
        target_points = 8000
        if len(x) > target_points:
            step = len(x) // target_points
            x_reduced = x[::step]
            t_reduced = np.linspace(0, len(x)/fs, len(x_reduced))
            fs_reduced = fs / step # Ajusta FS para o cálculo da derivada
        else:
            x_reduced = x
            t_reduced = np.linspace(0, len(x)/fs, len(x))
            fs_reduced = fs

        sinal_analitico = hilbert(x_reduced)
        fase_instantanea = np.unwrap(np.angle(sinal_analitico))
        
        # Derivada da fase = Frequência Angular. Divide por 2pi para Hz.
        freq_inst = (np.diff(fase_instantanea) / (2.0 * np.pi) * fs_reduced)
        
        # diff perde 1 ponto, ajustamos o tempo
        return t_reduced[1:], freq_inst