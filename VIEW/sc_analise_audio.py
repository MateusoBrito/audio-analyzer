import customtkinter as ctk
import sys
import os
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from CORE import graphic
from CORE.controls import Controls 
from tkinter import filedialog, messagebox
from VIEW.fr_barra_controle import ControlsSidebar
# --- NOVO: Importa a classe da nova sidebar ---
from VIEW.fr_barra_navegacao import NavigationSidebar

class AnalysisScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.logic_controller = Controls()

        # A tela principal continua responsável por carregar os ícones
        self.load_icons()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # --- Sidebar esquerda ---
        icons_for_sidebar = {
            "logo": self.icon_Logo,
            "upload": self.icon_upload,
            "analyze": self.icon_analyze,
            "export": self.icon_export,
            "menu": self.icon_menu
        }
        
        commands_for_sidebar = {
            "upload": self.upload_window,
            "analyze": self.analyze_audio,
            "export": self._lidar_com_exportacao,
            "menu": lambda: self.controller.show_frame("WelcomeScreen")
        }
        
        # 2. Cria a instância da sidebar, passando o master e os dicionários
        self.sidebar_left = NavigationSidebar(
            master=self, 
            icons=icons_for_sidebar, 
            commands=commands_for_sidebar
        )
        self.sidebar_left.grid(row=0, column=0, sticky="nswe")


        # --- Área central (gráficos) ---
        self.graph_container = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=0)
        self.graph_container.grid(row=0, column=1, sticky="nsew")
        self.build_graph_area()
        self.graphic = self.init_graphic_area()
        self.controls = controls.Controls(self.graphic)

        # --- Sidebar direita ---
        self.sidebar_right = ctk.CTkFrame(self, fg_color="#1e1e1e", width=220, corner_radius=0)
        self.sidebar_right.grid(row=0, column=2, sticky="nswe")
        self.sidebar_right.pack_propagate(False)
        self.controls_sidebar = ControlsSidebar(self.sidebar_right, self.controls)

    def load_icons(self):
        try:
            self.icon_upload = ctk.CTkImage(Image.open("images/upload.png"), size=(24, 24))
            self.icon_analyze = ctk.CTkImage(Image.open("images/Graph.png"), size=(24, 24))
            self.icon_export = ctk.CTkImage(Image.open("images/Export.png"), size=(24, 24))
            self.icon_menu = ctk.CTkImage(Image.open("images/Home.png"), size=(24, 24))
            self.icon_Logo = ctk.CTkImage(Image.open("images/Logo.png"), size=(101, 50))
        except FileNotFoundError as e:
            print(f"Erro ao carregar ícones: {e}")
            messagebox.showerror("Erro de Ícone", f"Não foi possível encontrar um ícone: {e}")
            self.icon_upload = self.icon_analyze = self.icon_export = self.icon_menu = self.icon_Logo = None

    # ---------- Sidebar Esquerda ----------
    def build_sidebar_left(self):
        logo_label = ctk.CTkLabel(
            self.sidebar_left,
            text="", 
            image=self.icon_Logo
        )
        logo_label.pack(pady=(20, 30), padx=10, anchor="center")

        buttons_data = {
            "   Carregar": (self.icon_upload, self.upload_window),
            "   Analisar": (self.icon_analyze, self.analyze_audio),
            "   Exportar": (self.icon_export, self._lidar_com_exportacao),
            "   Menu": (self.icon_menu, lambda: self.controller.show_frame("WelcomeScreen")), # <- VOLTA PARA O MENU
        }

        for i, (text, (icon, cmd)) in enumerate(buttons_data.items()):
            btn = ctk.CTkButton(
                self.sidebar_left,
                text=text,
                command=cmd,
                image=icon,
                compound="left",
                anchor="w",
                fg_color="#2b2b2b",
                text_color="white",
                hover_color="#5e5e5e",
                height=50,
                corner_radius=10,
                font=ctk.CTkFont(size=15, weight="bold"),
            )
            btn.pack(fill="x", padx=15, pady=(15 if i == 0 else 10), anchor="n")

    # ---------- Área de gráficos ----------
    def build_graph_area(self):
        self.graph_container.grid_rowconfigure((0, 1), weight=1)
        self.graph_container.grid_columnconfigure(0, weight=1)

        self.frame_fft = ctk.CTkFrame(self.graph_container, fg_color="#2b2b2b")
        self.frame_fft.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.frame_wave = ctk.CTkFrame(self.graph_container, fg_color="#2b2b2b")
        self.frame_wave.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def upload_window(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos WAV", "*.wav")])
        if not file_path:
            return
        try:
            success = self.logic_controller.load_file(file_path) 
            if success:
                self.analyze_audio()
            else:
                messagebox.showerror("Erro", "Não foi possível carregar o arquivo de áudio.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def analyze_audio(self):
        try:
            self.logic_controller.analyze_audio()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao analisar áudio: {str(e)}")

    #def apply_fft(self):
    #    fft_value = int(self.fft_slider.get())
    #    messagebox.showinfo("FFT", f"Resolução FFT definida para {fft_value}")

    def _lidar_com_exportacao(self):
        try:
            dir_path = filedialog.askdirectory(title="Selecione a pasta para salvar")
            if not dir_path:
                return

            nomes_arquivos = self.controls.exportar_graficos(dir_path)

            messagebox.showinfo(
                "Sucesso",
                "Gráficos exportados como:\n" + "\n".join(nomes_arquivos)
            )
        except ValueError as e:
            messagebox.showwarning("Aviso", str(e))
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro durante a exportação:\n{str(e)}")

    def init_graphic_area(self):
        gr = graphic.Graphic(self.frame_fft)
        self.canvas = gr.canvas
        widget = self.canvas.get_tk_widget()
        widget.configure(bg=self.frame_fft.cget("fg_color"), highlightthickness=0)
        return gr
