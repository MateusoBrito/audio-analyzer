import customtkinter as ctk
import sys
import matplotlib.pyplot as plt

from View.WelcomeScreen import WelcomeScreen
from View.AnalysisScreen import AnalysisScreen

# Configuração global do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela Principal
        self.title("Sound Analyzer Pro")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Sistema de Navegação (Stack de Frames) ---
        # Cria um container principal que ocupa toda a janela
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        
        # Configura o grid para que os frames se sobreponham (stack)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Inicializa as telas disponíveis
        # Passamos 'self' como o controller de navegação
        for F in (WelcomeScreen, AnalysisScreen):
            page_name = F.__name__
            frame = F(parent=self.container, nav_controller=self)
            self.frames[page_name] = frame
            
            # Coloca todos os frames no mesmo lugar (grid 0,0)
            frame.grid(row=0, column=0, sticky="nsew")

        # Inicia mostrando a tela de boas-vindas
        self.show_frame("WelcomeScreen")

    def show_frame(self, page_name):
        """Traz o frame solicitado para o topo da pilha."""
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):
        """Limpa recursos antes de fechar para evitar erros no terminal.""" 
        plt.close('all')
        self.quit()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()