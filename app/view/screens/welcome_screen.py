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
        super().__init__(parent, fg_color="#1a1a1a")
        self.nav_controller = nav_controller
        
        self.accent_color = "#ECEFF1"
        self.card_bg = "#212121"
        self.text_secondary = "#a0a0a0"
        
        # --- CARREGAMENTO DE IMAGENS ---
        self.icon_audio = None
        self.icon_emg = None
        self.logo_main = None
        self.logo_ppg = None
        self.logo_ufsj = None

        try:
            # Caminho base das imagens
            img_dir = "view/images"

            # 1. Ícones (Podem ser quadrados fixos mesmo, geralmente ícones são 1:1)
            self.icon_audio = ctk.CTkImage(Image.open(resource_path(os.path.join(img_dir, "audio_wave.png"))), size=(32, 32))
            self.icon_emg = ctk.CTkImage(Image.open(resource_path(os.path.join(img_dir, "emg_chip.png"))), size=(32, 32))

            # 2. Carregar Logos Respeitando Proporção
            # Definimos apenas a ALTURA desejada, a largura se ajusta sozinha
            
            # Logo Principal: Altura 80px
            self.logo_main = self.load_image_fixed_height(os.path.join(img_dir, "Logo.png"), fixed_height=130)
            
            # Logos Rodapé: Altura 50px (para ficarem alinhadas)
            self.logo_ppg = self.load_image_fixed_height(os.path.join(img_dir, "dmusic.jpeg"), fixed_height=70)
            self.logo_ufsj = self.load_image_fixed_height(os.path.join(img_dir, "logo-ufsj.png"), fixed_height=70)

        except Exception as e:
            print(f"Erro ao carregar imagens: {e}")

        self._build_ui()

    def load_image_fixed_height(self, relative_path, fixed_height):
        """
        Carrega uma imagem e calcula a largura automaticamente para não distorcer.
        """
        try:
            full_path = resource_path(relative_path)
            pil_img = Image.open(full_path)
            
            w_orig, h_orig = pil_img.size
            aspect_ratio = w_orig / h_orig
            
            new_width = int(fixed_height * aspect_ratio)
            
            return ctk.CTkImage(pil_img, size=(new_width, fixed_height))
        except Exception as e:
            print(f"Não foi possível carregar {relative_path}: {e}")
            return None

    def _build_ui(self):
        # --- CARD CENTRAL ---
        self.main_card = ctk.CTkFrame(
            self, 
            fg_color=self.card_bg, 
            corner_radius=25,
            border_width=2,
            border_color="#333333"
        )
        self.main_card.place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        content_frame.pack(padx=60, pady=40)

        # --- LOGO PRINCIPAL ---
        if self.logo_main:
            ctk.CTkLabel(content_frame, text="", image=self.logo_main).pack(pady=(0, 15))

        ctk.CTkLabel(
            content_frame, 
            text="BEM-VINDO AO SISTEMA", 
            font=("Roboto Medium", 12), 
            text_color=self.text_secondary,
            anchor="center"
        ).pack(pady=(0, 10))

        description = (
            "Explore o universo sonoro e bioelétrico.\n"
            "Visualize espectrogramas e dados em tempo real."
        )
        ctk.CTkLabel(
            content_frame, 
            text=description, 
            font=("Arial", 14), 
            justify="center",
            text_color=self.text_secondary
        ).pack(pady=(0, 30))

        # --- BOTÕES ---
        btn_audio = ctk.CTkButton(
            content_frame,
            text=" Análise de Áudio",
            image=self.icon_audio,
            compound="left",
            command=lambda: self.nav_controller.show_frame("AnalysisScreen"),
            width=280, height=55, font=("Arial", 15, "bold"),
            fg_color="#2b2b2b", hover_color="#3a3a3a",    
            border_width=2, border_color=self.accent_color, corner_radius=15
        )
        btn_audio.pack(pady=(0, 15))

        btn_emg = ctk.CTkButton(
            content_frame,
            text=" Análise EMG",
            image=self.icon_emg,
            compound="left",
            command=lambda: self.nav_controller.show_frame("EMGScreen"),
            width=280, height=55, font=("Arial", 15, "bold"),
            fg_color="#2b2b2b", text_color_disabled="#555555",
            border_width=2, border_color=self.accent_color, corner_radius=15
        )
        btn_emg.pack()

        ctk.CTkLabel(content_frame, text="v1.1.0", font=("Arial", 10), text_color="#404040").pack(pady=(20, 0))

        # --- RODAPÉ INSTITUCIONAL ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=25)

        # Container interno para centralizar as logos juntas
        logos_container = ctk.CTkFrame(footer_frame, fg_color="transparent")
        logos_container.pack()

        # Logo UFSJ (Esquerda)
        if self.logo_ufsj:
            lbl_ufsj = ctk.CTkLabel(logos_container, text="", image=self.logo_ufsj)
            lbl_ufsj.pack(side="left", padx=20)

        # Divisória vertical (opcional)
        separator = ctk.CTkFrame(logos_container, width=3, height=60, fg_color="#444444")
        separator.pack(side="left")

        # Logo PPGMUSI (Direita)
        if self.logo_ppg:
            lbl_ppg = ctk.CTkLabel(logos_container, text="", image=self.logo_ppg)
            lbl_ppg.pack(side="left", padx=20)