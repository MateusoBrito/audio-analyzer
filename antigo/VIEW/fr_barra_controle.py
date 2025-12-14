from tkinter import messagebox
import customtkinter as ctk
from VIEW.rename_dialog import RenameDialog

class ControlsSidebar:
    """
    Versão estilizada da barra de controles da direita, com componentes
    reutilizáveis e um design mais limpo.
    """
    # --- 1. CONSTANTES DE ESTILO ---
    # Mude as cores e fontes aqui para alterar o tema de toda a sidebar!
    FONT_FAMILY = "Sora"
    HEADER_FONT = (FONT_FAMILY, 15, "bold")
    BODY_FONT = (FONT_FAMILY, 12)
    LABEL_FONT = (FONT_FAMILY, 11)
    ENTRY_FONT = (FONT_FAMILY, 12)

    PRIMARY_COLOR = "#4A4D50"
    HOVER_COLOR = "#5E6164"
    BORDER_COLOR = "#3D3F42"
    TEXT_COLOR = "#DCE4EE"

    def __init__(self, master_frame, controls):
        self.controls = controls 
        self.frame = master_frame
        self._build_ui()

    # --- 2. MÉTODOS DE CONSTRUÇÃO DA UI (ORGANIZADORES) ---
    
    def _build_ui(self):
        """Constrói a UI em seções, usando os componentes estilizados."""
        self._add_divider()
        self._build_frequency_controls()
        self._add_divider()
        self._build_fft_controls()
        self._add_divider()
        self._build_action_buttons()

    def _add_divider(self):
        """Adiciona uma linha divisória para separar as seções."""
        divider = ctk.CTkFrame(self.frame, height=2, fg_color=self.BORDER_COLOR)
        divider.pack(fill="x", padx=8, pady=15)

    def _build_frequency_controls(self):
        self._create_section_header("Filtro de Frequência").pack(anchor="w", padx=10)

        # Usando o novo componente com Entry
        (min_frame, self.freq_min_slider, self.freq_min_entry) = self._create_slider_with_entry("Mín:", 20, 20000, "Hz")
        min_frame.pack(fill="x", padx=8, pady=(10, 5))

        (max_frame, self.freq_max_slider, self.freq_max_entry) = self._create_slider_with_entry("Máx:", 20, 20000, "Hz")
        max_frame.pack(fill="x", padx=8, pady=5)

    def _build_fft_controls(self):
        self._create_section_header("Amostragem FFT").pack(anchor="w", padx=8)
        
        self.fft_scale_entry = self._create_entry("1")
        self.fft_scale_entry.pack(fill="x", padx=10, pady=5)

    def _build_action_buttons(self):
        apply_btn = self._create_primary_button("Aplicar Mudanças", self._apply_all_changes)
        apply_btn.pack(pady=(5, 10), padx=8, fill="x")

        rename_btn = self._create_secondary_button("Trocar Nomes", self._open_rename_dialog)
        rename_btn.pack(pady=(5, 10), padx=8, fill="x")

        self.grid_btn = self._create_secondary_button("Grade: ON", self.controls.toggle_grid)
        self.grid_btn.pack(pady=(5, 10), padx=8, fill="x")

        btn_clear = self._create_secondary_button("Limpar Gráficos", self._limpar_button, hover_color="#C75450")
        btn_clear.pack(pady=5, padx=8, fill="x")

    def _open_rename_dialog(self):
        """Abre a janela para renomear todos os plots de uma vez."""
        current_plots = self.controls.plots
        if not current_plots:
            messagebox.showinfo("Aviso", "Nenhum gráfico carregado para renomear.")
            return

        dialog = RenameDialog(plots_data=current_plots)
        new_names = dialog.get_names() # Abre a janela e espera

        if new_names:
            self.controls.update_all_plot_labels(new_names)

    # --- 3. FÁBRICAS DE WIDGETS ESTILIZADOS ---

    def _create_section_header(self, text):
        return ctk.CTkLabel(self.frame, text=text, font=self.HEADER_FONT)
        
    def _create_slider_with_entry(self, title, from_, to, unit):
        """Cria um componente com slider e entry sincronizados."""
        main_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(main_frame, text=title, font=self.LABEL_FONT)
        title_label.grid(row=0, column=0, sticky="w")
        
        # 1. O label de valor agora é um CTkEntry
        value_entry = ctk.CTkEntry(
            main_frame,
            width=70,  # Largura fixa para o campo de texto
            font=self.ENTRY_FONT,
            justify="right"
        )
        value_entry.grid(row=0, column=1, sticky="e")
        value_entry.insert(0, f"{from_:.0f}")

        # 2. Funções de sincronização
        def update_entry(slider_value):
            """Atualiza o texto da Entry quando o slider é movido."""
            value_entry.delete(0, "end")
            value_entry.insert(0, f"{slider_value:.0f}")

        def update_slider(event=None):
            """Atualiza a posição do slider quando Enter é pressionado na Entry."""
            try:
                # Pega o valor, converte para float e limita entre min e max
                value = float(value_entry.get())
                value = max(from_, min(to, value))
                slider.set(value)
                # Atualiza a entry com o valor validado (caso o usuário digite algo fora do limite)
                update_entry(value) 
            except ValueError:
                # Se o usuário digitar algo que não é um número, volta para o valor atual do slider
                update_entry(slider.get())

        # 3. Criamos o slider e o conectamos à função que atualiza a entry
        slider = ctk.CTkSlider(main_frame, from_=from_, to=to, command=update_entry)
        slider.set(from_) # Define o valor inicial
        slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        
        # 4. Conectamos o evento <Return> (Enter) da entry à função que atualiza o slider
        value_entry.bind("<Return>", update_slider)
        
        return main_frame, slider, value_entry

    def _create_primary_button(self, text, command):
        return ctk.CTkButton(
            self.frame, text=text, command=command,
            fg_color=self.PRIMARY_COLOR, hover_color=self.HOVER_COLOR,
            text_color=self.TEXT_COLOR, corner_radius=8, height=35, font=self.BODY_FONT
        )
        
    def _create_secondary_button(self, text, command, hover_color=HOVER_COLOR):
        return ctk.CTkButton(
            self.frame, text=text, command=command,
            fg_color="transparent", hover_color=hover_color,
            border_width=2, border_color=self.BORDER_COLOR,
            text_color=self.TEXT_COLOR, corner_radius=8, height=35, font=self.BODY_FONT
        )

    def _create_entry(self, placeholder_text):
        entry = ctk.CTkEntry(
            self.frame, font=self.BODY_FONT,
            border_color=self.BORDER_COLOR, corner_radius=8, height=35
        )
        entry.insert(0, placeholder_text)
        return entry

    # --- Métodos de Callback (Lógica) ---

    def _apply_all_changes(self):
        """Lê TODOS os controles, valida, atualiza a lógica e redesenha."""
        try:
            # --- Etapa 1: Ler e validar todos os valores ---
            fi = float(self.freq_min_entry.get())
            fm = float(self.freq_max_entry.get())
            fft_scale = int(self.fft_scale_entry.get())

            if fi >= fm:
                messagebox.showerror("Erro", "A frequência mínima deve ser menor que a máxima.")
                return
            if fft_scale <= 0:
                messagebox.showwarning("Valor Inválido", "Amostragem deve ser um inteiro > 0.")
                return

            # --- Etapa 2: Atualizar todos os valores na classe Controls ---
            self.controls.fi = fi
            self.controls.fm = fm
            self.controls.fft_scale = fft_scale

            # Sincroniza os sliders com os valores digitados
            self.freq_min_slider.set(fi)
            self.freq_max_slider.set(fm)

            self.controls.analyze_audio()
            
            messagebox.showinfo("Sucesso", "Mudanças aplicadas e gráficos atualizados.")

        except ValueError:
            messagebox.showerror("Erro de Entrada", "Verifique se todos os campos contêm números válidos.")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")


    def _limpar_button(self):
        try:
            self.controls.limpar_tudo()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar gráficos: {str(e)}")