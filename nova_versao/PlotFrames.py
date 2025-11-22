import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import librosa.display
import numpy as np
import librosa.display

class BasePlotFrame(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master,fg_color="transparent")
        plt.style.use("dark_background")
        self.fig, self.ax =plt.subplots(facecolor='none')
        self.canvas = FigureCanvasTkAgg(self.fig,master=self)

        widget = self.canvas.get_tk_widget()
        widget.configure(bg='#2b2b2b', highlightthickness=0) 
        widget.pack(fill="both", expand=True)

    def clear(self):
        self.ax.clear()
    
    def draw(self):
        self.canvas.draw() # <--- Desenha IMEDIATAMENTE
        self.canvas.flush_events()

class FFTPlotFrame(BasePlotFrame):
    def __init__(self, master):
        super().__init__(master)
        self.ax_left = None
        self.ax_right = None
        self._init_subplots()
    
    def _init_subplots(self):
        """Cria os subplots 1x2"""
        self.clear()

        axs = self.fig.subplots(1, 2) 
        # Desempacota os eixos
        (self.ax_left, self.ax_right) = axs
        
        # Ajusta o espaçamento
        self.fig.subplots_adjust(wspace=0.3, left=0.1, right=0.95, bottom=0.15, top=0.9)
        
        # Define a cor dos eixos aqui, se necessário, ou deixa para o reset_axes
        self.ax_left.set_facecolor('none')
        self.ax_right.set_facecolor('none')
    
    def reset_axes(self, grid_enabled):
        """
        Limpa os eixos e reaplica o estilo visual (tema escuro, labels e grid).
        Recebe 'grid_enabled' do Controller.
        """
        for ax in [self.ax_left, self.ax_right]:
            ax.clear()

            # Cores de fundo e eixos (Estilização)
            ax.set_facecolor('none')
            ax.tick_params(colors="white", labelsize=9)
            ax.spines["bottom"].set_color("white")
            ax.spines["left"].set_color("white")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            # Labels
            ax.set_xlabel("Frequência (Hz)", fontsize=10, color="white", labelpad=8)
            ax.set_ylabel("Amplitude (normalizada)", fontsize=10, color="white", labelpad=8)

            # Grid (Usa o argumento passado)
            ax.grid(
                visible=grid_enabled,
                which="both",
                linestyle=":",
                linewidth=0.7,
                color="gray",
                alpha=0.4 if grid_enabled else 0.0,
            )

        # Títulos dos gráficos
        self.ax_left.set_title("Canal Esquerdo", fontsize=12, color="white", pad=12)
        self.ax_right.set_title("Canal Direito", fontsize=12, color="white", pad=12)

        # NOTA: Não chamamos self.canvas.draw() aqui! 
        # O AppController chama .draw() logo após o loop de plotagem.
        return

    def add_plot(self, freq, L, R, label, color):
        """Adiciona uma linha ao gráfico sem apagar as anteriores"""
        self.ax_left.plot(freq, L, color=color, label=label)
        self.ax_right.plot(freq, R, color=color, label=label)
        
        # Reaplica a legenda para incluir o novo item
        self.ax_left.legend(fontsize=8, framealpha=0.5)
        self.ax_right.legend(fontsize=8, framealpha=0.5)
    
class WaveformPlotFrame(BasePlotFrame):
    def plot(self, times, y_data, sr): 
        self.clear()
        ax = self.fig.add_subplot(111) 
        
        ax.set_facecolor('none')
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        # CORREÇÃO: Passando sr=sr para o librosa
        librosa.display.waveshow(y_data, sr=sr, ax=ax, color='steelblue')
        ax.set_title("Forma de Onda", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Amplitude", color="white")
        
        self.draw()

class RMSPlotFrame(BasePlotFrame):
    def plot(self, times, rms_data):
        self.clear()
        self.ax.plot(times, rms_data, color='orange')
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Amplitude RMS")
        self.ax.set_title("Envelope RMS")
        self.draw()

class SpectrogramPlotFrame(BasePlotFrame):
    def plot(self, S_db, sr):
        self.clear()
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', ax=self.ax, cmap='magma')
        self.ax.set_title("Espectrograma")
        self.draw()

class HilbertPlotFrame(BasePlotFrame):
    def plot(self, samples, envelope_data):
        self.clear()
        self.ax.plot(samples, envelope_data, color='purple')
        self.ax.set_xlabel("Amostras")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("Envelope de Hilbert")
        self.draw()