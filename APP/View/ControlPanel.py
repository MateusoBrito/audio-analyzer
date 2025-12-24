import customtkinter as ctk
from tkinter import messagebox

class ControlPanel(ctk.CTkFrame):
    """
    Painel Lateral Direito Simplificado:
    Focado apenas em filtros e controle de grade/limpeza.
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
        
        # --- REMOVIDO O MENU DE VISUALIZAÇÃO ---
        # Agora começamos direto pelos filtros
        
        # 1. Controles de Frequência (Min/Max)
        self._create_section_header("Filtro de frequência").pack(anchor="w", padx=15, pady=(20, 5))

        self.min_freq_frame, self.slider_min, self.entry_min = self._create_slider_group(
            "Mín (Hz):", 20, 20000, 20
        )
        self.min_freq_frame.pack(fill="x", padx=15, pady=5)

        self.max_freq_frame, self.slider_max, self.entry_max = self._create_slider_group(
            "Máx (Hz):", 20, 20000, 20000
        )
        self.max_freq_frame.pack(fill="x", padx=15, pady=5)

        self._add_divider()

        # 2. Controle de FFT Scale
        self._create_section_header("Resolução (FFT Scale)").pack(anchor="w", padx=15, pady=5)
        self.fft_scale_entry = ctk.CTkEntry(self, placeholder_text="1")
        self.fft_scale_entry.insert(0, "1")
        self.fft_scale_entry.pack(fill="x", padx=15, pady=5)

        self._add_divider()

        # 3. Botões de Ação
        
        # Botão Aplicar
        self.btn_apply = ctk.CTkButton(
            self, 
            text="Aplicar Parâmetros", 
            command=self._on_apply_click,
            fg_color="#4A4D50", 
            hover_color="#5E6164"
        )
        self.btn_apply.pack(fill="x", padx=15, pady=(15, 5))

        self.zoom_switch = ctk.CTkSwitch(
            self, 
            text="Modo Zoom", 
            command=self._on_toggle_zoom,
            onvalue=True, 
            offvalue=False,
            font=self.BODY_FONT
        )
        self.zoom_switch.pack(fill="x", padx=15, pady=10)
        # ---------------------------

        # Botão Resetar Zoom (Útil se o usuário se perder)
        self.btn_reset_zoom = ctk.CTkButton(
            self, 
            text="Resetar Zoom", 
            command=self._on_reset_zoom,
            fg_color="transparent", 
            border_width=1, 
            border_color="gray",
        )
        self.btn_reset_zoom.pack(fill="x", padx=15, pady=5)

        # Botão Grade
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
        line.pack(fill="x", padx=10, pady=15)
    
    def _create_slider_group(self, label_text, min_val, max_val, default_val):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x")

        lbl = ctk.CTkLabel(top_frame, text=label_text, font=self.BODY_FONT) # Adicionei text=label_text aqui que faltava no seu original
        lbl.pack(side="left")

        entry = ctk.CTkEntry(top_frame, width=60, font=self.BODY_FONT)
        entry.insert(0, str(default_val))
        entry.pack(side="right")

        def update_entry(val):
            entry.delete(0, "end")
            entry.insert(0, str(int(val)))

        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, command=update_entry)
        slider.set(default_val)
        slider.pack(fill="x", pady=(5, 0))

        return frame, slider, entry
    
    # --- Callbacks ---

    def _on_apply_click(self):
        try:
            fi = float(self.entry_min.get())
            fm = float(self.entry_max.get())
            fft_scale = int(self.fft_scale_entry.get())

            if fi >= fm:
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
    
    def _on_toggle_zoom(self):
        # O switch retorna 1 (True) ou 0 (False)
        is_active = self.zoom_switch.get()
        # Chama o controller (método que criamos antes)
        self.controller.active_plot_frame.set_zoom_mode(is_active)

    def _on_reset_zoom(self):
        self.controller.reset_zoom()
        # Se quiser desligar o switch ao resetar, descomente abaixo:
        # self.zoom_switch.deselect()
        # self.controller.active_plot_frame.set_zoom_mode(False)