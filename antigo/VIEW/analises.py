import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import librosa
import matplotlib.pyplot as plt

# Importa a classe do outro arquivo
from CORE.audio_graphics import Graphics

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Analisador de Áudio")
        self.geometry("900x700")
        self.audio_file = None

        # --- Frame Superior para Controles ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=10, padx=10, fill="x")

        self.select_button = ctk.CTkButton(self.control_frame, text="Selecionar Arquivo de Áudio", command=self.select_file)
        self.select_button.pack(side="left", padx=10, pady=10)
        
        self.file_label = ctk.CTkLabel(self.control_frame, text="Nenhum arquivo selecionado", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True, padx=10)

        # --- Frame Principal com Rolagem para os Gráficos ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Visualizações do Áudio")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.plot_canvases = []

    def select_file(self):
        """Abre uma janela para selecionar um arquivo de áudio."""
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo de áudio",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac"), ("All files", "*.*")]
        )
        if file_path:
            self.audio_file = file_path
            self.file_label.configure(text=file_path.split('/')[-1]) # Mostra só o nome do arquivo
            self.generate_plots()

    def clear_plots(self):
        """Remove os gráficos anteriores da tela."""
        for canvas in self.plot_canvases:
            canvas.get_tk_widget().destroy()
        self.plot_canvases.clear()
        # Garante que os objetos matplotlib sejam fechados para liberar memória
        plt.close('all')

    def generate_plots(self):
        """Carrega o áudio e gera todos os gráficos na interface."""
        if not self.audio_file:
            return

        self.clear_plots()

        try:
            y, sr = librosa.load(self.audio_file, sr=None)
            graficos = Graphics(y, sr)

            # Lista de métodos a serem chamados para gerar os gráficos
            plot_functions = [
                graficos.forma_onda,
                graficos.envelope_rms,
                graficos.espectrograma,
                graficos.espectro_frequencia,
                graficos.envelope_hilbert
            ]

            for func in plot_functions:
                fig = func()
                self.embed_plot(fig)

        except Exception as e:
            self.file_label.configure(text=f"Erro ao carregar o arquivo: {e}")

    def embed_plot(self, fig):
        """Incorpora uma figura Matplotlib no frame rolável."""
        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(pady=10, padx=10, fill="x", expand=True)
        self.plot_canvases.append(canvas)

if __name__ == "__main__":
    app = App()
    app.mainloop()