import customtkinter as ctk

class FileSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, filenames, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.filenames = filenames
        self.rows = []
        
        # Variável para o arquivo PRINCIPAL
        default_val = filenames[0] if filenames else ""
        self.main_file_var = ctk.StringVar(value=default_val)

        # Variáveis para os Gráficos (Dashboard)
        # Por padrão, todos vêm marcados (value=1)
        self.chart_vars = {
            "Waveform": ctk.IntVar(value=1),
            "Spectrogram": ctk.IntVar(value=1),
            "Pitch": ctk.IntVar(value=1),
            "SFFT3D": ctk.IntVar(value=1),
            "Hilbert": ctk.IntVar(value=1),
            "PitchSTFT": ctk.IntVar(value=1),
            "FFT": ctk.IntVar(value=1),
            "RMS": ctk.IntVar(value=1)
        }

        # Configurações da Janela
        self.title("Configurar Análise")
        self.geometry("700x700") # Aumentei um pouco para caber tudo
        self.resizable(True, True)
        
        self._build_ui()
        
        self.attributes("-topmost", True)
        self.after(10, self._set_focus)

    def _set_focus(self):
        self.lift()
        self.focus_force()
        self.grab_set()

    def _build_ui(self):
        # Container Principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- SEÇÃO 1: ESCOLHA DE GRÁFICOS ---
        ctk.CTkLabel(main_container, text="Selecione os Gráficos para Exibir:", 
                     font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        charts_frame = ctk.CTkFrame(main_container, fg_color="#2b2b2b")
        charts_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        # Cria checkboxes em grid (2 colunas)
        chart_names = [
            ("Forma de Onda (Tempo)", "Waveform"),
            ("Espectrograma (2D)", "Spectrogram"),
            ("Pitch / Afinação", "Pitch"),
            ("Espectro 3D (SFFT)", "SFFT3D"),
            ("Variação de Pitch (STFT)", "PitchSTFT"),
            ("Envoltória (Hilbert)", "Hilbert"),
            ("Espectro FFT (Freq)", "FFT"),
            ("RMS (Energia)", "RMS")
        ]

        for i, (label, key) in enumerate(chart_names):
            chk = ctk.CTkCheckBox(
                charts_frame, 
                text=label, 
                variable=self.chart_vars[key],
                font=("Arial", 12)
            )
            chk.grid(row=i//2, column=i%2, sticky="w", padx=20, pady=10)

        # --- SEÇÃO 2: SELEÇÃO DE ARQUIVOS ---
        ctk.CTkLabel(main_container, text="Selecione os Áudios:", 
                     font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # Cabeçalhos
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(0,5))
        
        ctk.CTkLabel(header_frame, text="Principal", width=60, font=("Arial", 11, "bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(header_frame, text="Comparar (FFT)", width=90, font=("Arial", 11, "bold"), anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Legenda", font=("Arial", 11, "bold"), anchor="w").pack(side="left", padx=5)

        # Scroll de Arquivos
        self.scroll_frame = ctk.CTkScrollableFrame(main_container, height=250)
        self.scroll_frame.pack(fill="both", expand=True, pady=5)

        if not self.filenames:
            ctk.CTkLabel(self.scroll_frame, text="Nenhum arquivo carregado!").pack(pady=20)

        for name in self.filenames:
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            # Radio (Principal)
            radio = ctk.CTkRadioButton(
                row_frame, text="", variable=self.main_file_var, value=name, width=30
            )
            radio.pack(side="left", padx=(5, 15))
            
            # Checkbox (Comparar)
            chk = ctk.CTkCheckBox(row_frame, text="", width=30)
            chk.select() 
            chk.pack(side="left", padx=(5, 15))
            
            # Entry (Nome)
            entry = ctk.CTkEntry(row_frame, height=30)
            entry.insert(0, name) 
            entry.pack(side="left", fill="x", expand=True)
            
            self.rows.append({"original": name, "check": chk, "entry": entry})

        # Botões de Ação
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(btn_frame, text="Confirmar", command=self._on_confirm, 
                      fg_color="#4A4D50", height=40).pack(side="right", padx=5)
                      
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, 
                      fg_color="transparent", border_width=1, height=40).pack(side="right", padx=5)

    def _on_confirm(self):
        # 1. Coleta dados dos arquivos
        selection_data = []
        main_file = self.main_file_var.get()
        
        for row in self.rows:
            if row['check'].get() == 1:
                original_name = row['original']
                display_name = row['entry'].get().strip() or original_name
                selection_data.append((original_name, display_name))
        
        # 2. Coleta dados dos gráficos (Quais estão ativos?)
        active_charts = []
        for key, var in self.chart_vars.items():
            if var.get() == 1:
                active_charts.append(key)

        # Retorna tudo para o callback
        self.callback(selection_data, main_file, active_charts)
        self.destroy()