import soundfile as sf
import os
import numpy as np
from scipy.fft import fft, fftfreq

class Controls():
    def __init__(self,graphic):
        self.current_file = None
        self.raw_data = None
        self.sample_rate = None
        self.plots = []
        self.grid_enabled = True  # Grade habilitada por padrão
        self.fft_scale = 1  # Fator de escala para amostragem FFT
        self.fi = 20
        self.fm = 20000
        self.graphic = graphic

    def load_file(self,file_path): 
        self.raw_data, self.sample_rate = sf.read(file_path, dtype="float32")
        self.file_name = os.path.basename(file_path)
        #self.analyze_audio()
        return

    def reset_axes(self, clear_plots=True):
        for ax in [self.graphic.ax_left, self.graphic.ax_right]:
            ax.clear()
            ax.set_facecolor('white')
            ax.set_xlabel("Frequência (Hz)", fontsize=10)
            ax.set_ylabel("Amplitude (normalizada)", fontsize=10)
            ax.grid(self.grid_enabled, which='both', linestyle=':', 
                    color='gray', alpha=0.5 if self.grid_enabled else 0.0)

        self.graphic.ax_left.set_title("Canal Esquerdo", fontsize=12, pad=10)
        self.graphic.ax_right.set_title("Canal Direito", fontsize=12, pad=10)

        if clear_plots:
            self.plots = []
        else:
            for plot_data in self.plots:
                freq, L, R, label, color = plot_data
                self.graphic.ax_left.plot(freq, L, color=color, label=label)
                self.graphic.ax_right.plot(freq, R, color=color, label=label)

        if self.plots:
            for ax in [self.graphic.ax_left, self.graphic.ax_right]:
                ax.legend(fontsize=8, framealpha=0.5)

        self.graphic.canvas.draw()


    def processar_audio(self, data, sample_rate, fi, fm):
        if data.ndim == 1:
            data = np.column_stack((data, data))
        
        n = len(data)
        # Aplica o fator de escala na amostragem
        step = int(self.fft_scale)
        if step < 1:
            step = 1
        
        freq = fftfreq(n, 1/sample_rate)[:n//2:step]
        
        L = np.abs(fft(data[:, 0]))[:n//2:step]
        R = np.abs(fft(data[:, 1]))[:n//2:step]
        
        mascara = (freq >= fi) & (freq <= fm)
        freq_filtrado = freq[mascara]
        
        L_norm = L[mascara] / (np.max(L[mascara]) or 1)
        R_norm = R[mascara] / (np.max(R[mascara]) or 1)
        
        return freq_filtrado, L_norm, R_norm

    def analyze_audio(self):
        if self.raw_data is None:
                return
                
        if self.fi >= self.fm:
            raise ValueError("Frequência mínima deve ser menor que a máxima")
        
        #self.reset_axes(clear_plots=not self.keep_var.get())
        self.reset_axes(clear_plots=False)
        # olha aqui
        freq, L, R = self.processar_audio(self.raw_data, self.sample_rate, self.fi, self.fm)
        color = f"C{len(self.plots)}"
        
        self.plots.append((freq, L, R, self.file_name, color))
        self.reset_axes(clear_plots=False)
        
        #self.log(f"Análise concluída: {self.file_name} ({self.fi}-{self.fm}Hz)")