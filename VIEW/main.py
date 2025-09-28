import customtkinter as ctk
from welcome_screen import WelcomeScreen
from analyse_audio_window import AnalysisScreen
import sys
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sound Analyzer")
        self.geometry("1600x900")

        # Container principal onde as telas (frames) serão empilhadas
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Cria as duas telas (Welcome e Analysis)
        for F in (WelcomeScreen, AnalysisScreen):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Começa mostrando a tela de boas-vindas
        self.show_frame("WelcomeScreen")

    def show_frame(self, page_name):
        '''Mostra um frame para a página solicitada'''
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
