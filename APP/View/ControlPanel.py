import customtkinter as ctk
from tkinter import messagebox

class ControlPanel(ctk.CTkFrame):
    """
    Painel Lateral Direito:
    Responsável por coletar configurações do usuário e enviá-las ao Controller.
    """

    FONT_FAMILY = "Sora"
    HEADER_FONT = (FONT_FAMILY, 14, "bold")
    BODY_FONT = (FONT_FAMILY, 12)

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1e1e1e", width=220, corner_radius=0)
        self.controller = controller

        self.pack_propagate(False)
        
        self._build_ui()

    def _build_ui(self):
        """Monta a interface verticalmente."""

        # 1. Seletor de Tipo de Análise
        self._create_section_header("Visualização").pack(anchor="w", padx=15,pady=(20,5))

        self.analysis_mode_menu = ctk.CTkOptionMenu(
            self,
            values=["Dashboard", "FFT", "Waveform", "Spectrogram", "RMS", "Hilbert"],
            command=self._on_analysis_change,
            fg_color="#4A4D50",
            button_color="#3D3F42",
            button_hover_color="#5E6164",
            font=self.BODY_FONT
        )
        self.analysis_mode_menu.set("Dashboard")
        self.analysis_mode_menu.pack(fill="x", padx=15, pady=5)

        self._add_divider()
        # 2. Controles de Frequência (Min/Max)

        self._create_section_header("Filtro de frequência").pack(anchor="w", padx=15,pady=5)

        self.min_freq_frame, self.slider_min, self.entry_min = self._create_slider_group(
            "Mín (Hz):", 20, 20000, 20
        )
        self.min_freq_frame.pack(fill="x", padx=15, pady=5)

        self.max_freq_frame, self.slider_max, self.entry_max = self._create_slider_group(
            "Máx (Hz):", 20, 20000, 20000
        )
        self.max_freq_frame.pack(fill="x", padx=15, pady=5)

        self._add_divider()
        #3. Controle de FFT Scale

        self._create_section_header("Resolução (FFT Scale)").pack(anchor="w", padx= 15, pady=5)
        self.fft_scale_entry = ctk.CTkEntry(self, placeholder_text="1")
        self.fft_scale_entry.insert(0,"1")
        self.fft_scale_entry.pack(fill="x",padx=15,pady=5)

        self._add_divider()
        #4. Botões de Ação

        # Botão Aplicar Parâmetros
        self.btn_apply = ctk.CTkButton(
            self, 
            text="Aplicar Parâmetros", 
            command=self._on_apply_click,
            fg_color="#4A4D50", 
            hover_color="#5E6164"
        )
        self.btn_apply.pack(fill="x", padx=15, pady=(15, 5))

        # Botão Toggle Grid
        self.btn_grid = ctk.CTkButton(
            self, 
            text="Grade: ON", 
            command=self._on_toggle_grid,
            fg_color="transparent", 
            border_width=1, 
            border_color="gray"
        )
        self.btn_grid.pack(fill="x", padx=15, pady=5)

        # Botão Limpar
        self.btn_clear = ctk.CTkButton(
            self, 
            text="Limpar Tela", 
            command=self._on_clear_click,
            fg_color="transparent",
            border_width=1,
            border_color="#C75450",
            text_color="#C75450",
            hover_color="#3a1c1c"
        )
        self.btn_clear.pack(fill="x", padx=15, pady=5)

    # -------------------------------------------------------------------------
    # SUPORTE 
    # -------------------------------------------------------------------------

    def _create_section_header(self, text):
        return ctk.CTkLabel(self, text=text, font=self.HEADER_FONT, text_color="#DCE4EE")

    def _add_divider(self):
        line = ctk.CTkFrame(self, height=2, fg_color="#3D3F42")
        line.pack(fill="x", padx=10,pady=15)
    
    def _create_slider_group(self, label_text, min_val, max_val, default_val):
        """Cria um frame contendo Label + Entry + Slider sincronizados."""
        frame = ctk.CTkFrame(self, fg_color="transparent")

        # Topo: Label e Entry
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x")

        lbl = ctk.CTkLabel(top_frame, width=60, font=self.BODY_FONT)
        lbl.pack(side="left")

        entry = ctk.CTkEntry(top_frame, width=60, font=self.BODY_FONT)
        entry.insert(0,str(default_val))
        entry.pack(side="right")

        # Slider
        def update_entry(val):
            entry.delete(0,"end")
            entry.insert(0, str(int(val)))

        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, command=update_entry)
        slider.set(default_val)
        slider.pack(fill="x", pady=(5,0))

        return frame, slider, entry
    
    # --- Lógica de Callbacks (Conectando ao Controller) ---

    def _on_analysis_change(self, selected_mode):
        """Chamado quando o usuário troca o tipo no Dropdown."""
        self.controller.set_analysis_type(selected_mode)
    
    def _on_apply_click(self):
        """Lê os inputs e manda para o Controller atualizar os parâmetros."""
        try:
            fi = float(self.entry_min.get())
            fm = float(self.entry_max.get())
            fft_scale = int(self.fft_scale_entry.get())

            if fi>=fm:
                messagebox.showwarning("Aviso", "Frequência mínima deve ser menor que a máxima.")
                return
            
            self.controller.update_analysis_params(fi=fi, fm=fm, fft_scale=fft_scale)
        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de usar apenas números nos campos.")
    
    def _on_toggle_grid(self):
        self.controller.toggle_grid()

        state = "ON" if self.controller.grid_enabled else "OFF"
        self.btn_grid.configure(text=f"Grade: {state}")
    
    def _on_clear_click(self):
        self.controller.clean()