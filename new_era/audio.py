from scipy.fft import fft, fftfreq
import numpy as np

class Audio:
    """
    Classe responsável por processar e analisar sinais de áudio,
    aplicando transformadas de Fourier e filtrando frequências.
    """

    def __init__(self, raw_data, sample_rate, fft_scale=1, fi=20, fm=20000):
        self.raw_data = raw_data
        self.sample_rate = sample_rate
        self.fft_scale = fft_scale
        self.fi = fi
        self.fm = fm
        

    def analyseAudio(self):
        """
        Analisa o áudio carregado no objeto, aplica uma análise espectral(FFT) no áudio atualmente armazenado e exibi os gráficos.
        """

        if self.raw_data is None or self.fi >= self.fm:
            return

        freq, L, R = self.__processAudio(self.raw_data, self.sample_rate, self.fi, self.fm)
        color = f"C{len(self.plots)}"
        self.plots.append((freq, L, R, self.file_name, color))

        print(freq)
        print(L)
        print(R)
        print(color)
        """
        self.graphic.reset_axes()
        for plot_data in self.plots:
            freq,L,R,label,colot = plot_data
            self.graphic.ax_left.plot(freq, L, color=color, label=label)
            self.graphic.ax_right.plot(freq, R, color=color, label=label)
        for ax in [self.graphic.ax_left, self.graphic.ax_right]:
            ax.legend(fontsize=8, framealpha=0.5)
        self.graphic.canvas.draw()
        """
        return freq, L, R


    def __processAudio(self, data, sample_rate, fi,fm):
        """
        Processa um sinal de áudio estéreo ou mono, aplicando FFT, filtrando uma faixa de frequências e normalizando o espectro.

        Parâmetros:
            data (np.ndarray): Amostras do áudio (1D para mono ou 2D para estéreo).
            sample_rate (int): Taxa de amostragem do áudio em Hz.
            fi (float): Frequência inicial do intervalo de análise (Hz).
            fm (float): Frequência final do intervalo de análise (Hz).

        Retorna:
            Freq_filtrado (np.ndarray): Frequências dentro do intervalo [fi,fm].
            L_norm (np.ndarray): Magnitudes normalizadas do canal esquerdo.
            R_norma (np.ndarray): Magnitudes normalizadas do canal direito.
        """
        if data.ndim == 1:
            data = np.column_stack((data,data))

        n=len(data)
        step = max(1, int(self.fft_scale))
        freq = fftfreq(n,1/sample_rate)[:n//2:step]

        L = np.abs(fft(data[:, 0]))[:n//2:step]
        R = np.abs(fft(data[:, 1]))[:n//2:step]

        mascara = (freq >= fi) & (freq <= fm)
        freq_filtrado = freq[mascara]
        L_norm = L[mascara] / (np.max(L[mascara]) or 1)
        R_norm = R[mascara] / (np.max(R[mascara]) or 1)

        return freq_filtrado, L_norm, R_norm