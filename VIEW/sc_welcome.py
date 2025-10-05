import customtkinter as ctk
from PIL import Image

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1a1a1a")
        self.controller = controller

        # Carregar ícones
        self.icon_audio = ctk.CTkImage(Image.open("images/audio_wave.png"), size=(40, 40))
        self.icon_emg = ctk.CTkImage(Image.open("images/emg_chip.png"), size=(40, 40))
        
        # Frame principal para centralizar o conteúdo
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True)

        # Container para o layout lado a lado
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(padx=50, pady=50)

        # --- Lado Esquerdo (Textos) ---
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=(0, 80), fill="y")

        welcome_label = ctk.CTkLabel(
            left_frame, 
            text="Olá, Seja Bem Vindo ao", 
            font=ctk.CTkFont(size=20, weight="normal"),
            text_color="#c0c0c0"
        )
        welcome_label.pack(anchor="w", pady=(0, 10))

        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        title_label_1 = ctk.CTkLabel(
            title_frame, 
            text="Sound", 
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#8a9cfa" # Um tom de azul claro
        )
        title_label_1.pack(side="left")

        title_label_2 = ctk.CTkLabel(
            title_frame, 
            text="Analyzer", 
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="white"
        )
        title_label_2.pack(side="left", padx=(10,0))

        description_text = (
            "Este aplicativo foi produzido com o intuito de estudar diferentes\n"
            "técnicas de tocar instrumentos. Analisando o seu resultado sonoro\n"
            "e as ativações musculares usadas."
        )
        description_label = ctk.CTkLabel(
            left_frame, 
            text=description_text,
            font=ctk.CTkFont(size=16),
            justify="left",
            text_color="#a0a0a0",
            wraplength=600
        )
        description_label.pack(anchor="w", pady=(20, 0))


        # --- Lado Direito (Botões) ---
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="y")
        
        # Botão Analisar Áudio
        btn_analyze_audio = ctk.CTkButton(
            right_frame,
            text="        Analisar\n        Áudio", # Espaços adicionados para simular padding
            image=self.icon_audio,
            compound="left",
            command=lambda: controller.show_frame("AnalysisScreen"),
            width=300,
            height=100,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3c3c3c",
            border_width=2,
            border_color="#5e5e5e",
            corner_radius=15,
            text_color_disabled="gray",
            anchor="w"
            # Removido: image_spacing e padx, que causavam o erro.
        )
        btn_analyze_audio.pack(pady=(0, 20))

        # Botão Analisar Eletromiógrado
        btn_analyze_emg = ctk.CTkButton(
            right_frame,
            text="        Analisar\n        Eletromiógrado", # Espaços adicionados para simular padding
            image=self.icon_emg,
            compound="left",
            width=300,
            height=100,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3c3c3c",
            border_width=2,
            border_color="#5e5e5e",
            corner_radius=15,
            state="disabled", # Desabilitado por enquanto
            text_color_disabled="gray",
            anchor="w"
            # Removido: image_spacing e padx, que causavam o erro.
        )
        btn_analyze_emg.pack(pady=(0, 20))

