import soundfile as sf
import os
import numpy as np
from scipy.fft import fft, fftfreq

class Controls:
    def __init__(self, graphic):
        self.graphic = graphic
        self.current_file = None
        self.raw_data = None
        self.sample_rate = None
        self.plots = []
        self.fft_scale = 1  # Fator de escala FFT
        self.fi = 20
        self.fm = 20000

    def toggle_grid(self):
        # Alterna o estado da grade no gráfico
        self.graphic.grid_enabled = not self.graphic.grid_enabled
        self.graphic.reset_axes()
        print(f"Grade dos gráficos: {'Ativada' if self.graphic.grid_enabled else 'Desativada'}")

    def load_file(self, file_path):
        self.raw_data, self.sample_rate = sf.read(file_path, dtype="float32")
        self.file_name = os.path.basename(file_path)

    def processar_audio(self, data, sample_rate, fi, fm):
        if data.ndim == 1:
            data = np.column_stack((data, data))

        n = len(data)
        step = max(1, int(self.fft_scale))
        freq = fftfreq(n, 1/sample_rate)[:n//2:step]

        L = np.abs(fft(data[:, 0]))[:n//2:step]
        R = np.abs(fft(data[:, 1]))[:n//2:step]

        mascara = (freq >= fi) & (freq <= fm)
        freq_filtrado = freq[mascara]
        L_norm = L[mascara] / (np.max(L[mascara]) or 1)
        R_norm = R[mascara] / (np.max(R[mascara]) or 1)

        return freq_filtrado, L_norm, R_norm

    def analyze_audio(self):
        if self.raw_data is None or self.fi >= self.fm:
            return

        freq, L, R = self.processar_audio(self.raw_data, self.sample_rate, self.fi, self.fm)
        color = f"C{len(self.plots)}"
        self.plots.append((freq, L, R, self.file_name, color))

        # Atualiza o gráfico
        self.graphic.reset_axes()  # Limpa e redesenha
        for plot_data in self.plots:
            freq, L, R, label, color = plot_data
            self.graphic.ax_left.plot(freq, L, color=color, label=label)
            self.graphic.ax_right.plot(freq, R, color=color, label=label)
        for ax in [self.graphic.ax_left, self.graphic.ax_right]:
            ax.legend(fontsize=8, framealpha=0.5)
        self.graphic.canvas.draw()

    def update_fft_scale(self, new_scale):
        if new_scale <= 0:
            raise ValueError("O valor deve ser maior que zero")
        self.fft_scale = new_scale
        if self.raw_data is not None:
            self.analyze_audio()
