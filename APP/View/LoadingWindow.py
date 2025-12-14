import customtkinter as ctk

class LoadingWindow(ctk.CTkToplevel):
    def __init__(self, parent, message="Aguarde..."):
        super().__init__(parent)
        
        # Remove a barra de título (janela estilo Popup/Overlay)
        self.overrideredirect(True)
        
        # Configurações visuais (Fundo escuro)
        self.configure(fg_color="#1e1e1e")
        
        # Tamanho do aviso
        req_width = 250
        req_height = 80
        
        # --- CÁLCULO DE CENTRALIZAÇÃO RELATIVA ---
        # Garante que temos as medidas atualizadas da janela pai
        parent.update_idletasks()
        
        # Pega a posição (X, Y) e tamanho (W, H) da janela principal do App
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calcula o centro exato
        x = parent_x + (parent_width // 2) - (req_width // 2)
        y = parent_y + (parent_height // 2) - (req_height // 2)
        
        # Aplica a geometria
        self.geometry(f"{req_width}x{req_height}+{x}+{y}")
        # -----------------------------------------
        
        # Garante que fique no topo de tudo
        self.attributes("-topmost", True)
        self.lift()
        
        # --- Layout Simples ---
        self.frame = ctk.CTkFrame(
            self, 
            fg_color="#2b2b2b", 
            border_width=2, 
            border_color="#a0a0a0", 
            corner_radius=10
        )
        self.frame.pack(fill="both", expand=True)
        
        self.lbl_msg = ctk.CTkLabel(
            self.frame, 
            text=message, 
            font=("Roboto Medium", 16), 
            text_color="white"
        )
        self.lbl_msg.place(relx=0.5, rely=0.5, anchor="center")