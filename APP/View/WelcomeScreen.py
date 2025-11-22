import customtkinter as ctk
from PIL import Image
import os

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, parent, nav_controller):
        super().__init__(parent, fg_color="#1a1a1a")
        self.nav_controller = nav_controller
        
        # Tenta carregar imagens (tratamento de erro básico)
        self.icon_audio = None
        self.icon_emg = None
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            img_path_dir = os.path.join(project_root, "images")
            
            self.icon_audio = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "audio_wave.png")), size=(40, 40))
            self.icon_emg = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "emg_chip.png")), size=(40, 40))
        except Exception as e:
            print(f"Aviso: Imagens da WelcomeScreen não encontradas: {e}")
            self.icon_audio = None
            self.icon_emg = None

        self._build_ui()

    def _build_ui(self):
        # Frame centralizador
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True)

        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(padx=50, pady=50)

        # --- Lado Esquerdo (Textos) ---
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=(0, 80), fill="y")

        ctk.CTkLabel(left_frame, text="Olá, Seja Bem Vindo ao", 
                     font=("Arial", 20), text_color="#c0c0c0").pack(anchor="w")

        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        ctk.CTkLabel(title_frame, text="Sound", font=("Arial", 70, "bold"), 
                     text_color="#8a9cfa").pack(side="left")
        ctk.CTkLabel(title_frame, text="Analyzer", font=("Arial", 70, "bold"), 
                     text_color="white").pack(side="left", padx=(10,0))

        description = (
            "Estude diferentes técnicas sonoras e ativações musculares.\n"
            "Visualize espectrogramas, formas de onda e muito mais."
        )
        ctk.CTkLabel(left_frame, text=description, font=("Arial", 16), justify="left",
                     text_color="#a0a0a0").pack(anchor="w", pady=(20, 0))

        # --- Lado Direito (Botões) ---
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="y")
        
        # Botão Analisar Áudio (Ação de Navegação)
        btn_audio = ctk.CTkButton(
            right_frame,
            text="   Analisar Áudio",
            image=self.icon_audio,
            compound="left",
            # AQUI ESTÁ A MÁGICA: Chama o método do main.py
            command=lambda: self.nav_controller.show_frame("AnalysisScreen"),
            width=280, height=90,
            font=("Arial", 20, "bold"),
            fg_color="#2b2b2b", hover_color="#3c3c3c",
            border_width=2, border_color="#5e5e5e", corner_radius=15
        )
        btn_audio.pack(pady=(0, 20))

        # Botão EMG (Desativado)
        btn_emg = ctk.CTkButton(
            right_frame,
            text="   Analisar EMG",
            image=self.icon_emg,
            compound="left",
            width=280, height=90,
            font=("Arial", 20, "bold"),
            fg_color="#2b2b2b", 
            state="disabled", # Ainda não implementado
            border_width=2, border_color="#5e5e5e", corner_radius=15
        )
        btn_emg.pack(pady=(0, 20))