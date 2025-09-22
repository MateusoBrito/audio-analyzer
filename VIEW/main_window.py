import customtkinter as ctk
from PIL import Image
from CORE import controls, graphic
from tkinter import filedialog, messagebox


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sound Analyzer")
        self.geometry("1100x600")

        # Estrutura principal: 3 colunas
        self.grid_columnconfigure(0, weight=0)   # Sidebar esquerda
        self.grid_columnconfigure(1, weight=1)   # Área de gráficos
        self.grid_columnconfigure(2, weight=0)   # Sidebar direita
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # --- Sidebar esquerda ---
        self.sidebar_left = ctk.CTkFrame(self, fg_color="#1e1e1e", width=150, corner_radius=0)
        self.sidebar_left.grid(row=0, column=0, sticky="nswe")
        self.build_sidebar_left()

        # --- Área central (gráficos) ---
        self.graph_container = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=0)
        self.graph_container.grid(row=0, column=1, sticky="nsew")
        self.build_graph_area()
        self.graphic = self.init_graphic_area()
        self.controls = controls.Controls(self.graphic)

        # --- Sidebar direita ---
        self.sidebar_right = ctk.CTkFrame(self, fg_color="#1e1e1e", width=180, corner_radius=0)
        self.sidebar_right.grid(row=0, column=2, sticky="nswe")
        self.build_sidebar_right()


    # ---------- Sidebar Esquerda ----------
    def build_sidebar_left(self):
        buttons = [
            ("📂 Carregar", self.upload_window),
            ("📊 Analisar", self.analyze_audio),
            ("💾 Exportar", self._lidar_com_exportacao),
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(
                self.sidebar_left,
                text=text,
                command=cmd,
                fg_color="#2b2b2b",
                text_color="white",
                hover_color="#5e5e5e",
                height=50,  # mais altos
                corner_radius=25,
                font=ctk.CTkFont(size=15, weight="bold"),  # fonte maior
            )
            btn.pack(fill="x", padx=15, pady=(12 if i == 0 else 10, 0), anchor="n")



    # ---------- Área de gráficos ----------
    def build_graph_area(self):
        self.graph_container.grid_rowconfigure((0, 1), weight=1)
        self.graph_container.grid_columnconfigure(0, weight=1)

        self.frame_fft = ctk.CTkFrame(self.graph_container, fg_color="#2b2b2b")
        self.frame_fft.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.frame_wave = ctk.CTkFrame(self.graph_container, fg_color="#202020")
        self.frame_wave.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def apply_frequency(self):
        fi = self.freq_min_slider.get()
        fm = self.freq_max_slider.get()
        if fi >= fm:
            messagebox.showerror("Erro", "Frequência mínima deve ser menor que a máxima.")
            return
        self.controls.fi = fi
        self.controls.fm = fm
        self.controls.analyze_audio()
        messagebox.showinfo("Frequências aplicadas", f"Min: {fi:.1f} Hz\nMax: {fm:.1f} Hz")


    def build_sidebar_right(self):
        # Modo escuro
        self.dark_mode_switch = ctk.CTkSwitch(self.sidebar_right, text="Modo Escuro")
        self.dark_mode_switch.pack(pady=10, padx=10)

        # --- Frequência ---
        ctk.CTkLabel(self.sidebar_right, text="Frequência (Hz)").pack(anchor="w", padx=10, pady=(10,0))

        # Frame para freq min
        freq_min_frame = ctk.CTkFrame(self.sidebar_right, fg_color="transparent")
        freq_min_frame.pack(fill="x", padx=10, pady=5)
        self.freq_min_slider = ctk.CTkSlider(freq_min_frame, from_=20, to=20000, number_of_steps=1000, command=self.update_freq_labels)
        self.freq_min_slider.set(20)
        self.freq_min_slider.pack(side="left", fill="x", expand=True)
        self.freq_min_label = ctk.CTkLabel(freq_min_frame, text=f"{self.freq_min_slider.get():.0f} Hz", width=60)
        self.freq_min_label.pack(side="right", padx=5)

        # Frame para freq max
        freq_max_frame = ctk.CTkFrame(self.sidebar_right, fg_color="transparent")
        freq_max_frame.pack(fill="x", padx=10, pady=5)
        self.freq_max_slider = ctk.CTkSlider(freq_max_frame, from_=20, to=20000, number_of_steps=1000, command=self.update_freq_labels)
        self.freq_max_slider.set(20000)
        self.freq_max_slider.pack(side="left", fill="x", expand=True)
        self.freq_max_label = ctk.CTkLabel(freq_max_frame, text=f"{self.freq_max_slider.get():.0f} Hz", width=60)
        self.freq_max_label.pack(side="right", padx=5)

        ctk.CTkButton(
            self.sidebar_right, 
            text="Aplicar Frequência", 
            command=self.apply_frequency
        ).pack(pady=10, padx=10, fill="x")

        # --- Amostragem ---
        ctk.CTkLabel(self.sidebar_right, text="Amostragem FFT (x)").pack(anchor="w", padx=10, pady=(10,0))
        self.fft_scale_entry = ctk.CTkEntry(self.sidebar_right)
        self.fft_scale_entry.insert(0, "1")
        self.fft_scale_entry.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            self.sidebar_right,
            text="Aplicar Amostragem",
            command=lambda: self.controls.update_fft_scale(int(self.fft_scale_entry.get()))
        ).pack(pady=10, padx=10, fill="x")

        # --- Grade ---
        self.grid_btn = ctk.CTkButton(
            self.sidebar_right,
            text="Grade: ON",
            command=self.controls.toggle_grid
        )
        self.grid_btn.pack(pady=10, padx=10, fill="x")

    # Função para atualizar os labels conforme o slider se move
    def update_freq_labels(self, _=None):
        self.freq_min_label.configure(text=f"{self.freq_min_slider.get():.0f} Hz")
        self.freq_max_label.configure(text=f"{self.freq_max_slider.get():.0f} Hz")



    # ---------- Funções de Controle ----------
    def upload_window(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos WAV", "*.wav")])
        if not file_path:
            return
        try:
            self.controls.load_file(file_path)
            messagebox.showinfo("Arquivo carregado", f"{file_path}")
            self.analyze_audio()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar áudio: {str(e)}")

    def analyze_audio(self):
        try:
            self.controls.analyze_audio()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao analisar áudio: {str(e)}")

    def apply_fft(self):
        fft_value = int(self.fft_slider.get())
        messagebox.showinfo("FFT", f"Resolução FFT definida para {fft_value}")

    def _lidar_com_exportacao(self):
        try:
            dir_path = filedialog.askdirectory(title="Selecione a pasta para salvar")
            if not dir_path:
                return

            nomes_arquivos = self.controls.exportar_graficos(dir_path)

            messagebox.showinfo(
                "Sucesso",
                "Gráficos exportados como:\n" + "\n".join(nomes_arquivos)
            )

        except ValueError as e:
            messagebox.showwarning("Aviso", str(e))
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro durante a exportação:\n{str(e)}")

    def init_graphic_area(self):
        gr = graphic.Graphic(self.graph_container)
        self.canvas = gr.canvas
        return gr





app = App()
app.mainloop()
