import customtkinter as ctk

class NavigationSidebar(ctk.CTkFrame):
    """
    Uma classe para a barra de navegação lateral esquerda.
    
    Esta classe é responsável por criar a interface da sidebar, incluindo o logo
    e os botões de ação. As funções que os botões executam são passadas
    pela classe pai (a tela principal).
    """
    def __init__(self, master, icons, commands, **kwargs):
        """
        Inicializa a barra de navegação.
        
        Args:
            master: O widget pai onde esta sidebar será colocada.
            icons (dict): Um dicionário contendo os objetos CTkImage necessários.
            commands (dict): Um dicionário mapeando ações (ex: 'upload') para as funções a serem chamadas.
        """
        super().__init__(master, fg_color="#1e1e1e", width=150, corner_radius=0, **kwargs)
        
        self.icons = icons
        self.commands = commands
        
        # REMOVIDO: O carregamento de ícones foi movido para a classe pai
        # self.load_icons() 
        
        self.build_ui()

    # REMOVIDO: A função load_icons não pertence a este componente reutilizável
    # def load_icons(self):
    #     ...

    def build_ui(self):
        """Constrói os elementos da interface da sidebar."""
        logo_label = ctk.CTkLabel(
            self,
            text="", 
            image=self.icons.get("logo") # Pega o ícone do dicionário
        )
        logo_label.pack(pady=(20, 30), padx=10, anchor="center")

        buttons_data = {
            "   Carregar": ("upload", "upload"),
            "   Analisar": ("analyze", "analyze"),
            "   Exportar": ("export", "export"),
            "   Menu": ("menu", "menu")
        }

        for i, (text, (icon_key, cmd_key)) in enumerate(buttons_data.items()):
            btn = ctk.CTkButton(
                self,
                text=text,
                command=self.commands.get(cmd_key), # Pega a função do dicionário de comandos
                image=self.icons.get(icon_key),     # Pega o ícone do dicionário de ícones
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