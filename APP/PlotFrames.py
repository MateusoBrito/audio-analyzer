import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import librosa.display
import numpy as np

# Cor de fundo do tema (Cinza Escuro do CTk)
THEME_COLOR = '#2b2b2b'

class BasePlotFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Cria a figura manualmente (sem criar eixos automaticamente)
        self.fig = plt.Figure(facecolor=THEME_COLOR, figsize=(5, 4), dpi=100)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        
        widget = self.canvas.get_tk_widget()
        # Configura o fundo do widget para a cor do tema
        widget.configure(bg=THEME_COLOR, highlightthickness=0) 
        widget.pack(fill="both", expand=True)

    def clear(self):
        # Limpa a FIGURA inteira
        self.fig.clear()
    
    def draw(self):
        # draw_idle é mais seguro para evitar erros de thread/inicialização
        self.canvas.draw_idle()

class FFTPlotFrame(BasePlotFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ax_left = None
        self.ax_right = None
        self._init_subplots()
    
    def _init_subplots(self):
        self.clear()
        
        # Cria os eixos manualmente
        axs = self.fig.subplots(1, 2)
        (self.ax_left, self.ax_right) = axs
        
        self.fig.subplots_adjust(wspace=0.3, left=0.1, right=0.95, bottom=0.15, top=0.9)
        
        # Define a cor de fundo dos eixos
        self.ax_left.set_facecolor(THEME_COLOR)
        self.ax_right.set_facecolor(THEME_COLOR)
    
    def reset_axes(self, grid_enabled):
        # Se os eixos foram apagados pelo clear(), recria eles
        if not self.fig.axes:
            self._init_subplots()

        for ax in [self.ax_left, self.ax_right]:
            ax.clear()
            ax.set_facecolor(THEME_COLOR) 

            ax.tick_params(colors="white", labelsize=9)
            ax.spines["bottom"].set_color("white")
            ax.spines["left"].set_color("white")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            ax.set_xlabel("Frequência (Hz)", fontsize=10, color="white", labelpad=8)
            ax.set_ylabel("Amplitude", fontsize=10, color="white", labelpad=8)

            ax.grid(
                visible=grid_enabled,
                which="both",
                linestyle=":",
                linewidth=0.7,
                color="gray",
                alpha=0.4 if grid_enabled else 0.0,
            )

        self.ax_left.set_title("Canal Esquerdo", fontsize=12, color="white", pad=12)
        self.ax_right.set_title("Canal Direito", fontsize=12, color="white", pad=12)

    def add_plot(self, freq, L, R, label, color):
        self.ax_left.plot(freq, L, color=color, label=label)
        self.ax_right.plot(freq, R, color=color, label=label)
        
        self.ax_left.legend(fontsize=8, framealpha=0.0, labelcolor='white')
        self.ax_right.legend(fontsize=8, framealpha=0.0, labelcolor='white')
    
class WaveformPlotFrame(BasePlotFrame):
    def plot(self, times, y_data, sr): 
        self.clear()
        ax = self.fig.add_subplot(111) 
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        librosa.display.waveshow(y_data, sr=sr, ax=ax, color='steelblue')
        ax.set_title("Forma de Onda", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Amplitude", color="white")
        
        self.draw()

class RMSPlotFrame(BasePlotFrame):
    def plot(self, times, rms_data):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.plot(times, rms_data, color='orange')
        ax.set_title("Envelope RMS", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Amplitude RMS", color="white")
        self.draw()

class SpectrogramPlotFrame(BasePlotFrame):
    def plot(self, S_db, sr):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', ax=ax, cmap='magma')
        
        cbar = self.fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.ax.yaxis.set_tick_params(color="white") 
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        ax.set_title("Espectrograma", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Frequência (Hz)", color="white")
        self.draw()

class HilbertPlotFrame(BasePlotFrame):
    def plot(self, samples, envelope_data):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.plot(samples, envelope_data, color='purple')
        ax.set_title("Envelope de Hilbert", color="white")
        ax.set_xlabel("Amostras", color="white")
        ax.set_ylabel("Amplitude", color="white")
        self.draw()

class MetricsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.labels = {}
        self.grid_columnconfigure((0, 1, 2), weight=1)
        metrics_keys = [
            ("Duração", "duration"), ("Taxa de Amostragem", "sr"),
            ("Fator de Crista", "crest"), ("Centróide Médio", "centroid"),
            ("Roll-off Médio", "rolloff"), ("Frequência Fund. (F0)", "f0")
        ]
        for i, (title, key) in enumerate(metrics_keys):
            frame = ctk.CTkFrame(self, fg_color="#333333", corner_radius=6)
            frame.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            lbl_title = ctk.CTkLabel(frame, text=title, font=("Arial", 11, "bold"), text_color="gray")
            lbl_title.pack(pady=(5, 0))
            self.labels[key] = ctk.CTkLabel(frame, text="--", font=("Arial", 16, "bold"), text_color="white")
            self.labels[key].pack(pady=(0, 5))

    def update_metrics(self, data):
        self.labels["duration"].configure(text=f"{data['duration']:.2f} s")
        self.labels["sr"].configure(text=f"{data['sr']} Hz")
        self.labels["crest"].configure(text=f"{data['crest_factor']:.2f}")
        self.labels["centroid"].configure(text=f"{data['centroid']:.2f} Hz")
        self.labels["rolloff"].configure(text=f"{data['rolloff']:.2f} Hz")
        self.labels["f0"].configure(text=f"{data['f0']:.2f} Hz")

class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Dashboard de Análise")
        self.frames = {}
        
        self.metrics_view = MetricsFrame(self)
        self.metrics_view.pack(fill="x", expand=True, pady=(0, 10), padx=5)
        
        # 1. FFT com altura aumentada (600px) e propagação desligada
        self.frames['FFT'] = FFTPlotFrame(self, height=600)
        self.frames['FFT'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['FFT'].pack_propagate(False)

        # 2. Outros gráficos com altura padrão
        self.frames['Waveform'] = WaveformPlotFrame(self)
        self.frames['Waveform'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Waveform'].configure(height=250) 

        self.frames['Spectrogram'] = SpectrogramPlotFrame(self)
        self.frames['Spectrogram'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Spectrogram'].configure(height=250)
        
        self.frames['RMS'] = RMSPlotFrame(self)
        self.frames['RMS'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['RMS'].configure(height=250)

        self.frames['Hilbert'] = HilbertPlotFrame(self)
        self.frames['Hilbert'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Hilbert'].configure(height=250)

    def get_frame(self, name):
        return self.frames.get(name)

    def clear(self):
        for frame in self.frames.values():
            frame.clear()

    def draw(self):
        for frame in self.frames.values():
            frame.draw()
    
    def update_metrics(self, data):
        self.metrics_view.update_metrics(data)