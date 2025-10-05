import customtkinter as ctk
from tkinter import filedialog
import matplotlib.pyplot as plt

from VIEW.fr_graficos_fixos import fr_graficos

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Analisador de Áudio Principal")
        self.geometry("900x700")

        # Frame para os controles (botão, etc.)
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=10, padx=10, fill="x")

        self.select_button = ctk.CTkButton(self.control_frame, text="Selecionar Arquivo de Áudio", command=self.select_file)
        self.select_button.pack(pady=10, padx=10)

        # Container onde o frame dos gráficos será inserido
        self.graficos_container = ctk.CTkFrame(self, fg_color="transparent")
        self.graficos_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.current_graficos_frame = None # Referência para o frame atual

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if not file_path:
            return

        # Se já existe um frame de gráficos, destrói ele antes de criar um novo
        if self.current_graficos_frame:
            self.current_graficos_frame.destroy()

        # Cria uma instância do nosso componente fr_graficos
        # O 'master' é o container que definimos para ele
        self.current_graficos_frame = fr_graficos(master=self.graficos_container, audio_file=file_path)
        self.current_graficos_frame.pack(fill="both", expand=True)

    def on_closing(self):
        plt.close('all')
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()