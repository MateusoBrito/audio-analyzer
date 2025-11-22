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
        self.canvas.draw()
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
        
        # CORREÇÃO: Criar o eixo explicitamente
        ax = self.fig.add_subplot(111)
        
        # Estilização manual (obrigatória agora)
        ax.set_facecolor('none')
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Plotagem
        ax.plot(times, rms_data, color='orange')
        ax.set_title("Envelope RMS", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Amplitude RMS", color="white")
        
        self.draw()

class SpectrogramPlotFrame(BasePlotFrame):
    def plot(self, S_db, sr):
        self.clear()
        
        # CORREÇÃO: Criar o eixo explicitamente
        ax = self.fig.add_subplot(111)
        
        # Estilização manual para o tema escuro
        ax.set_facecolor('none')
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        # No espectrograma, geralmente mantemos as bordas ou ajustamos conforme gosto,
        # mas para consistência, vou deixar só esquerda/baixo visíveis:
        ax.spines["top"].set_visible(False) 
        ax.spines["right"].set_visible(False)
        
        # Plotagem
        # Nota: Passamos 'ax=ax' (o eixo que acabamos de criar)
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', ax=ax, cmap='magma')
        
        # Adiciona a barra de cores (opcional, mas recomendado para espectrogramas)
        cbar = self.fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.ax.yaxis.set_tick_params(color="white") # Cor dos ticks da barra
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white') # Cor do texto da barra
        
        ax.set_title("Espectrograma", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Frequência (Hz)", color="white")
        
        self.draw()

class HilbertPlotFrame(BasePlotFrame):
    def plot(self, samples, envelope_data):
        self.clear()
        
        # CORREÇÃO: Criar o eixo explicitamente
        ax = self.fig.add_subplot(111)
        
        # Estilização manual
        ax.set_facecolor('none')
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Plotagem
        ax.plot(samples, envelope_data, color='purple')
        ax.set_title("Envelope de Hilbert", color="white")
        ax.set_xlabel("Amostras", color="white")
        ax.set_ylabel("Amplitude", color="white")
        
        self.draw()

class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Dashboard de Análise")
        
        self.frames = {}

        self.frames['FFT'] = FFTPlotFrame(self)
        self.frames['FFT'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['FFT'].configure(height=750)
        self.frames['FFT'].pack_propagate(False)

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
        """Limpa todos os sub-gráficos do dashboard."""
        for frame in self.frames.values():
            frame.clear()

    def draw(self):
        """Manda todos os sub-gráficos desenharem."""
        for frame in self.frames.values():
            frame.draw()