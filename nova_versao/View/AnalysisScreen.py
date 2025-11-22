import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os

from AppController import AppController
from View.ControlPanel import ControlPanel

class AnalysisScreen(ctk.CTkFrame):
    def __init__(self, parent, nav_controller):
        """
        Args:
            parent: O widget pai (geralmente o container do App principal).
            nav_controller: O controlador de NAVEGAÇÃO (para voltar ao Menu).
        """
        super().__init__(parent)
        self.nav_controller = nav_controller

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.load_icons()

        self._build_left_sidebar()
        self._build_center_area()

        self.logic_controller = AppController(self.graph_container)

        self._build_right_sidebar()

        self.logic_controller.set_analysis_type("FFT")

    def load_icons(self):
        """Carrega ícones ou define None se falhar."""
        self.icons = {}
        self.icons = {}
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            img_path_dir = os.path.join(project_root, "images")

            # Carrega as imagens usando o caminho absoluto
            self.icons['upload'] = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "upload.png")), size=(24, 24))
            self.icons['analyze'] = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "Graph.png")), size=(24, 24))
            self.icons['export'] = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "Export.png")), size=(24, 24))
            self.icons['home'] = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "Home.png")), size=(24, 24))
            
            # Logo (tamanho diferente)
            self.icons['logo'] = ctk.CTkImage(Image.open(os.path.join(img_path_dir, "Logo.png")), size=(101, 50))
            
        except Exception as e:
            print(f"Erro ao carregar ícones: {e}")
            # Define ícones como None para evitar que o programa feche
            for key in ['upload', 'analyze', 'export', 'home', 'logo']:
                self.icons[key] = None

    # -------------------------------------------------------------------------
    # CONSTRUÇÃO DA UI
    # -------------------------------------------------------------------------

    def _build_left_sidebar(self):
        """Coluna 0: Menu de Ações Gerais"""
        self.sidebar_left = ctk.CTkFrame(self, width=150, corner_radius=0, fg_color="#1e1e1e")
        self.sidebar_left.grid(row=0, column=0, sticky="nsew")

        if self.icons['logo']:
            logo_label = ctk.CTkLabel(self.sidebar_left, text="", image=self.icons['logo'])
            logo_label.pack(pady=(20,30), padx=10)
        else:
            ctk.CTkLabel(self.sidebar_left, text="SOUND\nANALYZER", font=("Arial", 16, "bold")).pack(pady=30)

        self._create_menu_btn("Carregar", self.icons['upload'], self._on_upload_click)
        self._create_menu_btn("Analisar", self.icons['analyze'], self._on_analyze_click)
        self._create_menu_btn("Exportar", self.icons['export'], self._on_export_click)

        ctk.CTkFrame(self.sidebar_left, fg_color="transparent").pack(expand=True)
        self._create_menu_btn("Menu", self.icons['home'], lambda: self.nav_controller.show_frame("WelcomeScreen"))
    
    def _build_center_area(self):
        """Coluna 1: Container Vazio para os Gráficos"""
        self.graph_container = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=0)
        self.graph_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    def _build_right_sidebar(self):
        """Coluna 2: Painel de Controles Específicos"""
        self.right_panel = ControlPanel(self, self.logic_controller)
        self.right_panel.grid(row=0, column=2, sticky="nsew")

    def _create_menu_btn(self, text, icon, command):
        btn = ctk.CTkButton(
            self.sidebar_left,
            text=f"  {text}",
            command=command,
            image=icon,
            compound="left",
            anchor="w",
            fg_color="transparent",
            text_color="#DCE4EE",
            hover_color="#5e5e5e",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn.pack(fill="x", padx=10, pady=5)
        return btn
    
    # -------------------------------------------------------------------------
    # CALLBACKS (A Ponte entre a UI e o Controller)
    # -------------------------------------------------------------------------

    def _on_upload_click(self):
        """Abre diálogo de arquivo e manda o controller carregar."""
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos WAV","*.wav"),("MP3","*.mp3")])
        if file_path:
            self.logic_controller.load_file(file_path)
            # Feedback visual opcional: mudar o título ou status
    
    def _on_analyze_click(self):
        """Adiciona o arquivo carregado ao gráfico atual."""
        self.logic_controller.add_active_file_to_plot()
    
    def _on_export_click(self):
        """Exporta os gráficos atuais."""
        dir_path = filedialog.askdirectory(title="Selecione a pasta para salvar")
        if dir_path:
            try:
                self.logic_controller.export_graph(dir_path)
                messagebox.showinfo("Sucesso", "Gráficos exportados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na exportação: {e}")
