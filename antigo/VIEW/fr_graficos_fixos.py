import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import librosa
import matplotlib.pyplot as plt

from CORE.audio_graphics import Graphics

class fr_graficos(ctk.CTkFrame):
    def __init__(self, master, audio_file, **kwargs):
        super().__init__(master, **kwargs)
        
        self.audio_file = audio_file
        self.plot_canvases = []

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Visualizações do Áudio")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.gerar_figuras()

    def gerar_figuras(self):
        """Carrega o áudio e gera todos os gráficos neste frame."""
        try:
            y, sr = librosa.load(self.audio_file, sr=None)
            graficos = Graphics(y, sr) 

            funcoes_plot = [
                graficos.espectrograma,
                graficos.forma_onda,
                graficos.envelope_rms,
                graficos.espectro_frequencia,
                graficos.envelope_hilbert
            ]

            for funcao in funcoes_plot:
                fig = funcao()
                self.embed_plot(fig)

        except Exception as e:
            error_label = ctk.CTkLabel(self.scrollable_frame, text=f"Erro ao carregar o arquivo: {e}", text_color="red")
            error_label.pack(pady=20)
    
    def embed_plot(self, fig):
        """Incorpora uma figura Matplotlib no frame rolável."""
        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(pady=10, padx=10, fill="x", expand=True)
        self.plot_canvases.append(canvas)