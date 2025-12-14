import customtkinter as ctk

# A correção está aqui: trocamos CTkDialog por CTkToplevel
class RenameDialog(ctk.CTkToplevel):
    def __init__(self, plots_data):
        super().__init__()
        self.title("Renomear Gráficos")
        self.attributes("-topmost", True) # Mantém a janela no topo

        self.new_names = None
        self.entries = []

        # Frame rolável para a lista
        scroll_frame = ctk.CTkScrollableFrame(self, label_text="Edite os nomes das linhas")
        scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Cria uma linha para cada gráfico
        for i, plot_data in enumerate(plots_data):
            label_text = plot_data[3]
            color = plot_data[4]

            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", expand=True, pady=4, padx=4)
            
            color_swatch = ctk.CTkFrame(row_frame, width=20, height=20, fg_color=color, border_width=0, corner_radius=4)
            color_swatch.pack(side="left", padx=(5, 8), pady=5)

            entry = ctk.CTkEntry(row_frame, font=("Sora", 12))
            entry.insert(0, label_text)
            entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=5)
            self.entries.append(entry)

        # Botões de ação
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ok_button = ctk.CTkButton(button_frame, text="Salvar Alterações", command=self._on_save)
        ok_button.pack(side="right")
        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1)
        cancel_button.pack(side="right", padx=10)

    def _on_save(self):
        self.new_names = [entry.get().strip() for entry in self.entries]
        self.destroy()

    def get_names(self):
        # Este método faz a janela aparecer e esperar pelo input do usuário
        self.grab_set() # Torna a janela modal (bloqueia a janela principal)
        self.wait_window() # Espera até que a janela seja destruída
        return self.new_names