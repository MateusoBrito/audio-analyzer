import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

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
    
    def set_grid(self, enabled):
        """Ativa/Desativa a grade de forma segura."""
        for ax in self.fig.axes:
            if enabled:
                ax.grid(True, linestyle=':', linewidth=0.7, color="gray", alpha=0.4)
            else:
                ax.grid(False)
        self.canvas.draw_idle()

    def clear(self):
        # Limpa a FIGURA inteira
        self.fig.clear()
    
    def draw(self):
        # draw_idle é mais seguro para evitar erros de thread/inicialização
        self.canvas.draw_idle()

class FFTPlotFrame(BasePlotFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ax = None
        self._init_subplots()
    
    def _init_subplots(self):
        self.clear()
        # Cria um ÚNICO eixo (Mono)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.1, right=0.95, bottom=0.15, top=0.9)
        self.ax.set_facecolor(THEME_COLOR)
    
    def reset_axes(self, grid_enabled):
        if not self.fig.axes:
            self._init_subplots()

        self.ax.clear()
        self.ax.set_facecolor(THEME_COLOR) 
        self.ax.tick_params(colors="white", labelsize=9)
        
        for spine in self.ax.spines.values():
            if spine.spine_type in ['bottom', 'left']:
                spine.set_color("white")
            else:
                spine.set_visible(False)

        self.ax.set_xlabel("Frequência (Hz)", fontsize=10, color="white", labelpad=8)
        self.ax.set_ylabel("Amplitude", fontsize=10, color="white", labelpad=8)
        self.ax.set_title("Espectro de Frequências (Mono)", fontsize=12, color="white", pad=12)

        self.ax.grid(
            visible=grid_enabled,
            which="both",
            linestyle=":",
            linewidth=0.7,
            color="gray",
            alpha=0.4 if grid_enabled else 0.0,
        )

    def add_plot(self, freq, mag, label, color):
        self.ax.plot(freq, mag, color=color, label=label, linewidth=1.5)
        self.ax.legend(fontsize=9, framealpha=0.0, labelcolor='white')

class WaveformPlotFrame(BasePlotFrame):
    def plot(self, times, y_data): 
        self.clear()
        ax = self.fig.add_subplot(111) 
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        
        ax.plot(times, y_data, color='#4FC3F7', linewidth=0.6)
        ax.set_title("Forma de Onda", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Amplitude", color="white")
        
        self.draw()

class SpectrogramPlotFrame(BasePlotFrame):
    def plot(self, t, f, S_db):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            if spine.spine_type in ['bottom', 'left']:
                spine.set_color("white")
            else:
                spine.set_visible(False)
        
        # Usando pcolormesh para suportar eixos cortados (fmin/fmax)
        img = ax.pcolormesh(t, f, S_db, shading='gouraud', cmap='inferno')
        
        cbar = self.fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.ax.yaxis.set_tick_params(color="white") 
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        ax.set_title("Espectrograma", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Frequência (Hz)", color="white")
        
        self.draw()

class PitchPlotFrame(BasePlotFrame):
    def plot(self, times, f0_data):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            if spine.spine_type in ['bottom', 'left']:
                spine.set_color("white")
            else:
                spine.set_visible(False)

        # Plot da linha de Pitch (Azul igual ao cliente)
        ax.plot(times, f0_data, color='#448AFF', linewidth=1.2, label="F0 (Hz)")
        
        ax.set_title("Variação da Afinação (Pitch)", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Frequência (Hz)", color="white")
        
        # Limita eixo Y visualmente se tiver dados
        if len(f0_data) > 0:
            max_f0 = np.max(f0_data)
            if max_f0 > 0:
                ax.set_ylim(0, max_f0 * 1.2)
            
        self.draw()

class SFFT3DPlotFrame(BasePlotFrame):
    def plot(self, T, F, Zxx_mag):
        self.clear()
        
        ax = self.fig.add_subplot(111, projection='3d')
        ax.set_facecolor(THEME_COLOR)
        
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.set_tick_params(colors='white')
            axis.label.set_color('white')
            axis.pane.fill = False 
            axis.pane.set_edgecolor('white')
            
        surf = ax.plot_surface(
            T, F, Zxx_mag, 
            cmap='viridis', 
            edgecolor='none', 
            rstride=8,  # Aumente aqui (era 2)
            cstride=8,  # Aumente aqui (era 2)
            antialiased=False # Desligar antialias também ajuda na performance
        )
        
        ax.set_title("Espectro 3D (SFFT)", color="white")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Freq (Hz)")
        ax.set_zlabel("dB")
        
        ax.view_init(elev=30, azim=-60)
        
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
    
    def reset(self):
        for label in self.labels.values():
            label.configure(text="--")

class HilbertFreqPlotFrame(BasePlotFrame):
    def plot(self, times, freq_data):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            if spine.spine_type in ['bottom', 'left']:
                spine.set_color("white")
            else:
                spine.set_visible(False)

        # --- SEU ESTILO: COR VERDE ---
        ax.plot(times, freq_data, color='green', linewidth=0.8, label='Freq. Instantânea')
        
        ax.set_title("Pitch estimado via Transformada de Hilbert", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Frequência (Hz)", color="white")
        
        # Limita eixo Y para visualização melhor (opcional, remove ruídos extremos)
        ax.set_ylim(0, 22000) 
        
        self.draw()

class HilbertPlotFrame(BasePlotFrame):
    def plot(self, samples, envelope_data):
        self.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(THEME_COLOR)
        
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            if spine.spine_type in ['bottom', 'left']:
                spine.set_color("white")
            else:
                spine.set_visible(False)

        # --- SEU ESTILO: VERMELHO TRACEJADO ---
        ax.plot(samples, envelope_data, color='red', linestyle='--', label='Envoltória')
        
        ax.legend(fontsize=8, framealpha=0.0, labelcolor='white')
        ax.set_title("Sinal e sua Envoltória", color="white")
        ax.set_xlabel("Tempo (s)", color="white")
        ax.set_ylabel("Amplitude", color="white")
        
        self.draw()

class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Dashboard de Análise")
        self.frames = {}
        
        # 1. Métricas
        self.metrics_view = MetricsFrame(self)
        self.metrics_view.pack(fill="x", expand=True, pady=(0, 10), padx=5)
        
        # 2. FFT (Mono)
        self.frames['FFT'] = FFTPlotFrame(self, height=600)
        self.frames['FFT'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['FFT'].pack_propagate(False)

        self.frames['SFFT3D'] = SFFT3DPlotFrame(self, height=500) # Mais alto para caber bem
        self.frames['SFFT3D'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['SFFT3D'].configure(height=500)

        # 4. Espectrograma
        self.frames['Spectrogram'] = SpectrogramPlotFrame(self)
        self.frames['Spectrogram'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Spectrogram'].configure(height=250)

        # 3. Waveform
        self.frames['Waveform'] = WaveformPlotFrame(self)
        self.frames['Waveform'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Waveform'].configure(height=250) 
        
        # 5. Pitch (NOVO)
        self.frames['Pitch'] = PitchPlotFrame(self)
        self.frames['Pitch'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Pitch'].configure(height=250)
        
        # 6. RMS
        self.frames['RMS'] = RMSPlotFrame(self)
        self.frames['RMS'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['RMS'].configure(height=250)

        # Adicione o Gráfico Verde aqui
        self.frames['HilbertFreq'] = HilbertFreqPlotFrame(self)
        self.frames['HilbertFreq'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['HilbertFreq'].configure(height=250)

        # O HilbertPlotFrame (Vermelho) já deve estar 
        self.frames['Hilbert'] = HilbertPlotFrame(self)
        self.frames['Hilbert'].pack(fill="x", expand=True, pady=5, padx=5)
        self.frames['Hilbert'].configure(height=250)

    def get_frame(self, name):
        """Retorna o frame solicitado pelo nome."""
        return self.frames.get(name)

    def clear(self):
        """Limpa todos os gráficos e métricas."""
        for frame in self.frames.values():
            frame.clear()
        self.metrics_view.reset()

    def draw(self):
        """Redesenha todos os gráficos."""
        for frame in self.frames.values():
            frame.draw()
    
    def update_metrics(self, data):
        self.metrics_view.update_metrics(data)
    
    def update_all_grids(self, enabled):
        """Comanda todos os gráficos do dashboard a mudar a grade."""
        for frame in self.frames.values():
            if hasattr(frame, 'set_grid'):
                frame.set_grid(enabled)