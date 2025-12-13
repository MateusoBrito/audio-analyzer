import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os

from AppController import AppController
from View.ControlPanel import ControlPanel
from View.FileSelectionDialog import FileSelectionDialog
from View.RecordingDialog import RecordingDialog

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

        self.logic_controller.set_analysis_type("Dashboard")

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
        self._create_menu_btn("Gravar", self.icons.get('none'), self._on_record_click)

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
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos WAV","*.wav"),("MP3","*.mp3")])
        if file_path:
            self.logic_controller.load_file(file_path)
            messagebox.showinfo("Carregado", f"Arquivo carregado:\n{os.path.basename(file_path)}")
    
    def _on_analyze_click(self):
        """Abre a janela de seleção."""
        available_files = list(self.logic_controller.loaded_files.keys())
        if not available_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")
            return

        FileSelectionDialog(
            parent=self, 
            filenames=available_files, 
            callback=self._on_files_selected
        )

    def _on_files_selected(self, selection_data, main_file):
        """
        Recebe:
        - selection_data: Lista de tuplas [(nome_orig, apelido), ...] para o FFT
        - main_file: String com o nome do arquivo principal para Onda/Spec/etc
        """
        self.logic_controller.update_plot_selection(selection_data, main_file)
        
    def _on_export_click(self):
        """Exporta os gráficos atuais."""
        dir_path = filedialog.askdirectory(title="Selecione a pasta para salvar")
        if dir_path:
            try:
                self.logic_controller.export_graph(dir_path)
                messagebox.showinfo("Sucesso", "Gráficos exportados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na exportação: {e}")
    
    def _on_record_click(self):
        """Abre a janela de gravação"""
        RecordingDialog(self, callback=self._on_recording_saved)

    def _on_recording_saved(self, filepath):
        """Chamado quando a gravação é salva com sucesso"""
        # 1. Carrega o arquivo no Controller
        self.logic_controller.load_file(filepath)
        
        # 2. (Opcional) Já joga ele direto na tela para ver o resultado
        # Se quiser que ele apenas carregue e não plote, remova a linha abaixo.
        self.logic_controller.add_active_file_to_plot()
        
        messagebox.showinfo("Sucesso", f"Áudio gravado e carregado:\n{os.path.basename(filepath)}")
