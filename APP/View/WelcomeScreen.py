import customtkinter as ctk
from PIL import Image
import os
import sys

def resource_path(relative_path):
    """Obtém o caminho absoluto para o recurso."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, parent, nav_controller):
        super().__init__(parent, fg_color="#1a1a1a") # Fundo geral escuro
        self.nav_controller = nav_controller
        
        # Definição de Cores do Tema
        self.accent_color = "#ECEFF1"  # Azul suave
        self.card_bg = "#212121"       # Cinza um pouco mais claro que o fundo
        self.text_secondary = "#a0a0a0"
        
        # Carregamento de imagens
        self.icon_audio = None
        self.icon_emg = None
        try:
            img_audio = resource_path(os.path.join("images", "audio_wave.png"))
            self.icon_audio = ctk.CTkImage(Image.open(img_audio), size=(32, 32)) # Ícones ligeiramente menores para elegância
            img_emg = resource_path(os.path.join("images", "emg_chip.png"))
            self.icon_emg = ctk.CTkImage(Image.open(img_emg), size=(32, 32))          
        except Exception as e:
            print(f"Aviso: Imagens não encontradas: {e}")

        self._build_ui()

    def _build_ui(self):
        # --- CARD CENTRAL ---
        # Usamos place para garantir que fique EXATAMENTE no centro, independente do tamanho da janela
        self.main_card = ctk.CTkFrame(
            self, 
            fg_color=self.card_bg, 
            corner_radius=25,
            border_width=2,
            border_color="#333333" # Borda sutil
        )
        self.main_card.place(relx=0.5, rely=0.5, anchor="center")

        # Container interno para dar padding (margem interna)
        content_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        content_frame.pack(padx=60, pady=50)

        # --- SEÇÃO DE CABEÇALHO ---
        ctk.CTkLabel(
            content_frame, 
            text="BEM-VINDO AO", 
            font=("Roboto Medium", 14), 
            text_color=self.text_secondary,
            anchor="center"
        ).pack(pady=(0, 10))

        # Frame para juntar as duas cores do título no centro
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame, text="Sound", font=("Arial", 48, "bold"), 
            text_color=self.accent_color
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame, text="Analyzer", font=("Arial", 48, "bold"), 
            text_color="white"
        ).pack(side="left", padx=(8,0))

        # Descrição
        description = (
            "Explore o universo sonoro e bioelétrico.\n"
            "Visualize espectrogramas e dados em tempo real."
        )
        ctk.CTkLabel(
            content_frame, 
            text=description, 
            font=("Arial", 16), 
            justify="center",
            text_color=self.text_secondary
        ).pack(pady=(0, 40))

        # --- SEÇÃO DE BOTÕES ---
        
        # Botão Principal (Com destaque de borda e cor)
        btn_audio = ctk.CTkButton(
            content_frame,
            text=" Análise de Áudio",
            image=self.icon_audio,
            compound="left",
            command=lambda: self.nav_controller.show_frame("AnalysisScreen"),
            width=320, 
            height=60,
            font=("Arial", 16, "bold"),
            fg_color="#2b2b2b", 
            hover_color="#3a3a3a",    
            border_width=2, 
            border_color=self.accent_color, # AQUI: Borda azul para indicar ação principal
            corner_radius=15
        )
        btn_audio.pack(pady=(0, 15))

        # Botão Secundário (Desativado / Mais discreto)
        btn_emg = ctk.CTkButton(
            content_frame,
            text=" Análise EMG",
            image=self.icon_emg,
            compound="left",
            width=320, 
            height=60,
            font=("Arial", 16, "bold"),
            fg_color="transparent",        # Fundo transparente para diferenciar hierarquia
            text_color_disabled="#555555",
            border_width=2, 
            border_color="#333333",        # Borda cinza escuro
            state="disabled", 
            corner_radius=15
        )
        btn_emg.pack()

        # Rodapézinho estético (opcional)
        ctk.CTkLabel(
            content_frame,
            text="v1.0.0",
            font=("Arial", 10),
            text_color="#404040"
        ).pack(pady=(30, 0))