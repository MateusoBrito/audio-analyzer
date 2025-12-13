import customtkinter as ctk

class FileSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, filenames, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.filenames = filenames
        self.rows = []
        
        # Variável para rastrear qual arquivo é o PRINCIPAL
        default_val = filenames[0] if filenames else ""
        self.main_file_var = ctk.StringVar(value=default_val)

        # Configurações da Janela
        self.title("Gerenciar Áudios")
        self.geometry("600x600")
        self.resizable(True, True) # Deixar redimensionável ajuda a "acordar" a janela as vezes
        
        # 1. Constrói a UI PRIMEIRO
        self._build_ui()
        
        # 2. Configurações de Foco e Modal (O Pulo do Gato)
        self.attributes("-topmost", True)
        
        # Usamos .after para esperar 10ms até a janela desenhar antes de travar o foco
        # Isso resolve o problema da tela preta/travada
        self.after(10, self._set_focus)

    def _set_focus(self):
        self.lift()
        self.focus_force()
        self.grab_set()

    def _build_ui(self):
        # Container principal com padding para não colar nas bordas
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_container, text="Selecione os áudios para visualização:", 
                     font=("Arial", 16, "bold")).pack(pady=(0, 15))

        # Cabeçalhos
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(0,5))
        
        # Labels alinhadas
        ctk.CTkLabel(header_frame, text="Principal", width=60, font=("Arial", 12, "bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(header_frame, text="Plotar", width=50, font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=15)
        ctk.CTkLabel(header_frame, text="Legenda (Nome)", font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=5)

        # Área de Rolagem (Expandida)
        self.scroll_frame = ctk.CTkScrollableFrame(main_container)
        # CORREÇÃO DE VISUAL: fill="both", expand=True garante que ocupe a tela
        self.scroll_frame.pack(fill="both", expand=True, pady=5)

        if not self.filenames:
            ctk.CTkLabel(self.scroll_frame, text="Nenhum arquivo carregado!").pack(pady=20)

        # Criação das linhas
        for name in self.filenames:
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # 1. Radio Button (PRINCIPAL)
            radio = ctk.CTkRadioButton(
                row_frame, 
                text="", 
                variable=self.main_file_var, 
                value=name, 
                width=30,
                border_width_checked=6,
                border_width_unchecked=3
            )
            radio.pack(side="left", padx=(5, 15))
            
            # 2. Checkbox (PLOTAR NO FFT)
            chk = ctk.CTkCheckBox(row_frame, text="", width=30)
            chk.select() 
            chk.pack(side="left", padx=(5, 15))
            
            # 3. Entry (RENOMEAR)
            entry = ctk.CTkEntry(row_frame, height=35)
            entry.insert(0, name) 
            entry.pack(side="left", fill="x", expand=True)
            
            self.rows.append({
                "original": name,
                "check": chk,
                "entry": entry
            })

        # Botões
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(btn_frame, text="Confirmar", command=self._on_confirm, 
                      fg_color="#4A4D50", height=40).pack(side="right", padx=5)
                      
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, 
                      fg_color="transparent", border_width=1, height=40).pack(side="right", padx=5)

    def _on_confirm(self):
        selection_data = []
        main_file = self.main_file_var.get()
        
        for row in self.rows:
            is_checked = row['check'].get()
            
            if is_checked == 1:
                original_name = row['original']
                display_name = row['entry'].get().strip() or original_name
                selection_data.append((original_name, display_name))
        
        self.callback(selection_data, main_file)
        self.destroy()