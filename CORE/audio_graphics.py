import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

plt.style.use('dark_background')

class Graphics:
    """
    Uma classe para gerar e exibir diversas visualizações de um sinal de áudio.

    Esta classe encapsula a lógica para criar gráficos comuns em análise de áudio,
    como a forma de onda, espectrograma, envelope de energia, entre outros.

    Atributos:
        y (np.ndarray): O sinal de áudio como uma série temporal.
        sr (int): A taxa de amostragem do sinal de áudio (em Hz).
    """

    def __init__(self, y, sr):
        self.y = y
        self.sr = sr
   
    def _create_figure(self, title, xlabel, ylabel):
        """Método auxiliar para criar uma figura e eixos padronizados."""
        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#2b2b2b')
        fig.suptitle(title, color='white')
        ax.set_xlabel(xlabel, color='white')
        ax.set_ylabel(ylabel, color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor('#3c3c3c') # Cor de fundo do plot
        return fig, ax

    def forma_onda(self):
        """
        1️⃣ Gráfico da forma de onda (domínio do tempo)

        Exibe a amplitude do sinal de áudio ao longo do tempo. Esta é a representação
        mais direta de um sinal de áudio, mostrando as variações de pressão da onda sonora.

        - Eixo X: Tempo (s)
        - Eixo Y: Amplitude do sinal
        """
        fig, ax = self._create_figure("Forma de Onda", "Tempo (s)", "Amplitude")
        librosa.display.waveshow(self.y, sr=self.sr, ax=ax, color='steelblue')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        return fig

    def envelope_rms(self, frame_length=2048, hop_length=512):
        """
        2️⃣ Envelope de Energia RMS (Root Mean Square)

        Calcula e exibe a energia média (RMS) do sinal ao longo do tempo.
        Este gráfico suaviza a forma de onda, fornecendo uma visão clara da
        dinâmica e do volume percebido do áudio, ignorando as oscilações rápidas.

        Args:
            frame_length (int): O tamanho da janela (em amostras) para calcular o RMS.
            hop_length (int): O número de amostras para avançar entre os frames.

        - Eixo X: Tempo (s)
        - Eixo Y: Amplitude RMS (energia)
        """
        fig, ax = self._create_figure("Envelope RMS", "Tempo (s)", "Amplitude RMS")

        rms = librosa.feature.rms(y=self.y, frame_length=frame_length, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=hop_length)

        ax.plot(times, rms, color='orange')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        return fig

    def espectro_frequencia(self):
        """
        3️⃣ Espectro de Frequência (FFT)

        Decompõe o sinal de áudio em suas frequências constituintes usando a
        Transformada Rápida de Fourier (FFT). Este gráfico mostra a intensidade
        de cada frequência presente no áudio como um todo (visão estática).

        - Eixo X: Frequência (Hz)
        - Eixo Y: Magnitude (intensidade da frequência)
        """
        fig, ax = self._create_figure("Espectro de Frequência (FFT)", "Frequência (Hz)", "Magnitude")

        fft = np.fft.fft(self.y)
        magnitude = np.abs(fft)[:len(fft)//2]
        freqs = np.fft.fftfreq(len(fft), 1/self.sr)[:len(fft)//2]

        ax.plot(freqs, magnitude, color='green')
        #ax.set_yscale('log')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        return fig

    def espectrograma(self):
        """
        4️⃣ Espectrograma

        Visualiza a evolução do conteúdo de frequência do sinal ao longo do tempo.
        É uma das ferramentas mais poderosas para análise de áudio, pois combina
        três dimensões em um único gráfico.

        - Eixo X: Tempo (s)
        - Eixo Y: Frequência (Hz), em escala logarítmica para melhor visualização.
        - Cor: Amplitude ou energia da frequência (dB), onde cores mais quentes
                 indicam maior intensidade.
        """
        fig, ax = self._create_figure("Espectrograma", "Tempo (s)", "Frequência (Hz)")

        S = librosa.stft(self.y)
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

        img = librosa.display.specshow(S_db, sr=self.sr, x_axis='time', y_axis='log', ax=ax, cmap='magma')
        fig.colorbar(img, ax=ax, format='%+2.0f dB', label='Amplitude (dB)')
        fig.tight_layout(rect=[0, 0, 0.9, 0.96])
        return fig

    def envelope_hilbert(self):
        """
        5️⃣ Envelope de Amplitude via Transformada de Hilbert

        Calcula o envelope de amplitude (contorno) do sinal usando a Transformada
        de Hilbert. Este método fornece a "amplitude instantânea" para cada
        amostra, resultando em um contorno mais preciso que o RMS, especialmente
        útil para capturar transientes rápidos.

        - Eixo X: Amostras (proporcional ao tempo)
        - Eixo Y: Amplitude instantânea
        """
        fig, ax = self._create_figure("Envelope de Hilbert", "Amostras", "Amplitude")

        analytic_signal = hilbert(self.y)
        amplitude_envelope = np.abs(analytic_signal)

        ax.plot(amplitude_envelope, color='purple')
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        return fig