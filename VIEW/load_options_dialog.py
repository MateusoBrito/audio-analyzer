import customtkinter as ctk

class LoadOptionsDialog(ctk.CTkToplevel):
    def __init__(self, default_name=""):
        super().__init__()

        self.title("Opções do Gráfico")
        self.geometry("350x220")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel) # Lida com o fechamento no "X"
        self.attributes("-topmost", True) # Mantém a janela no topo

        self.result = None
        self.selected_color = "#1f77b4" # Cor padrão (azul do Matplotlib)

        # --- Widgets ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        # Campo para o nome
        ctk.CTkLabel(main_frame, text="Nome da Linha do Gráfico:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(main_frame)
        self.name_entry.pack(fill="x", pady=(0, 15))
        self.name_entry.insert(0, default_name)

        # Seletor de cor
        ctk.CTkLabel(main_frame, text="Cor da Linha:").pack(anchor="w")
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        color_frame.pack(fill="x")

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
        for color in colors:
            btn = ctk.CTkButton(
                color_frame, text="", width=30, height=30, corner_radius=5,
                fg_color=color, hover_color=color,
                command=lambda c=color: self._select_color(c)
            )
            btn.pack(side="left", padx=4)

        # Botões de confirmação
        ok_button = ctk.CTkButton(main_frame, text="OK", command=self._on_ok)
        ok_button.pack(side="right", padx=(10, 0), pady=(20, 0))
        cancel_button = ctk.CTkButton(main_frame, text="Cancelar", command=self._on_cancel, fg_color="transparent", border_width=1)
        cancel_button.pack(side="right", pady=(20, 0))

    def _select_color(self, color):
        self.selected_color = color
        print(f"Cor selecionada: {self.selected_color}")

    def _on_ok(self, event=None):
        self.result = {
            "name": self.name_entry.get().strip(),
            "color": self.selected_color
        }
        self.destroy()

    def _on_cancel(self, event=None):
        self.result = None
        self.destroy()

    def get_input(self):
        """Mostra a janela e espera até que seja fechada."""
        self.wait_window()
        return self.result