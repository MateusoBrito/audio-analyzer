import customtkinter as ctk
from PIL import Image
from CORE import controls, graphic
from tkinter import filedialog, messagebox, ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sound Analyzer")
        self.geometry("900x500")
        self.config(bg='#f0f0f0')

        # Configure grid da janela principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_ui()

    def setup_ui(self):
        self.graphic = self.graphic_area()
        self.controls = controls.Controls(self.graphic)
        self.header_area()

    def header_area(self):
        self.header = ctk.CTkFrame(self, fg_color="#F4F4F4", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

        self.header.grid_columnconfigure((1, 2, 3, 4, 5, 6), weight=1) 

        img = ctk.CTkImage(
            light_image=Image.open("images/Logo.png"),
            dark_image=Image.open("images/Logo.png"),
            size=(60, 30)
        )

        label_img = ctk.CTkLabel(self.header, image=img, text="")
        label_img.grid(row=0, column=0, padx=15, pady=5)

        self.frequency_buttons(self.header)
        self.upload = self.upload_button(self.header)
        self.analyze = self.analyze_button(self.header)
        self.sampling_scale_buttons(self.header)
        self.grid_buttons(self.header)
        self.export_button(self.header)

    
    def upload_window(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos WAV", "*.wav")])
        if not file_path:
            return
        try:
            self.controls.load_file(file_path)
            self.analyze.configure(state=ctk.NORMAL)
            self.analyze_audio()
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar áudio: {str(e)}")
        

    def style_buttons(self):
        """Retorna um dicionário com o estilo padrão para botões transparentes."""
        return {
            "fg_color": "transparent",
            "text_color": "black",
            "hover_color": "#E5E5E5",
            "corner_radius": 5
        }

    def upload_button(self, header):
        btn_style = self.style_buttons()
        btn = ctk.CTkButton(
            header,
            text="Carregar WAV",
            command=self.upload_window,
            **btn_style
        )
        btn.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        return btn
    
    def analyze_audio(self):
        try:
            self.controls.analyze_audio()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao analisar áudio: {str(e)}")

    def analyze_button(self, header):
        btn_style = self.style_buttons()
        btn = ctk.CTkButton(header, text="Analisar", command=self.analyze_audio, state=ctk.DISABLED,**btn_style)
        btn.grid(row=0, column=2, padx=5, pady=10,sticky = "ew")
        return btn
    
    def frequency_buttons(self, header):
        fi = 20
        fm = 20000
        self.popup_visible = False

        btn_style = self.style_buttons()
        self.freq_button = ctk.CTkButton(header, text="Frequência", command=self.open_freq_window, **btn_style)
        self.freq_button.grid(row=0, column=3, padx=5, pady=10,sticky = "ew")

        # Frame popup (flutuante)
        self.popup_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#e0e0e0")

        # Sliders
        ctk.CTkLabel(self.popup_frame, text="Freq. Min (Hz)", text_color="black").grid(row=0, column=0, pady=(5,0))
        self.slider_min = ctk.CTkSlider(self.popup_frame, from_=20, to=20000, number_of_steps=1000)
        self.slider_min.set(fi)
        self.slider_min.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.popup_frame, text="Freq. Max (Hz)" , text_color="black").grid(row=1, column=0, pady=(5,0))
        self.slider_max = ctk.CTkSlider(self.popup_frame, from_=20, to=20000, number_of_steps=1000)
        self.slider_max.set(fm)
        self.slider_max.grid(row=1, column=1, padx=10, pady=5)

        # Botão aplicar
        self.apply_btn = ctk.CTkButton(self.popup_frame, text="Aplicar", command=self.apply_freq,
                                      fg_color="#0078D7", text_color="white", hover_color="#106EBE")
        self.apply_btn.grid(row=2, column=0, columnspan=2, pady=10)


    def open_freq_window(self):
        if self.popup_visible:
            self.popup_frame.place_forget()
            self.popup_visible = False
        else:
            # Pega posição do botão em relação à janela
            bx = self.freq_button.winfo_rootx() - self.winfo_rootx()
            by = self.freq_button.winfo_rooty() - self.winfo_rooty() + self.freq_button.winfo_height()

            # Mostra popup logo abaixo do botão
            self.popup_frame.place(x=bx, y=by)
            self.popup_visible = True

    def apply_freq(self):
        fi = self.slider_min.get()
        fm = self.slider_max.get()
        if fi >= fm:
            messagebox.showerror("Erro", "Frequência mínima deve ser menor que a máxima.")
            return
        self.controls.fi = fi
        self.controls.fm = fm
        self.controls.analyze_audio()
        messagebox.showinfo("OK", f"Frequências aplicadas:\nMin: {fi:.1f} Hz\nMax: {fm:.1f} Hz")
        self.open_freq_window()  # fecha após aplicar

    def sampling_scale_buttons(self, header):
        fft_frame = ctk.CTkFrame(header, corner_radius=5, fg_color="#F4F4F4")
        fft_frame.grid(row=0, column=4, padx=5, pady=10, sticky="ew")

        fft_frame.grid_columnconfigure(1, weight=1) 
        fft_frame.grid_columnconfigure(2, weight=1) 

        ctk.CTkLabel(fft_frame, text="Amostragem FFT (x):", text_color="black").grid(row=0, column=0, sticky="e")

        self.entry_fft_scale = ctk.CTkEntry(fft_frame, width=50)
        self.entry_fft_scale.insert(0, "1")
        self.entry_fft_scale.grid(row=0, column=1, padx=5)

        apply_btn = ctk.CTkButton(
            fft_frame, 
            text="Aplicar", 
            command=lambda: self.controls.update_fft_scale(int(self.entry_fft_scale.get())),
            fg_color="#0078D7", text_color="white", hover_color="#106EBE", width=60
        )
        apply_btn.grid(row=0, column=2, padx=5, sticky="ew")

    def grid_buttons(self, header):
        btn_style = self.style_buttons()
        self.controls.grid_btn = ctk.CTkButton(
            self.header,
            text="Grade: ON",
            command=self.controls.toggle_grid,
            **btn_style
        )
        self.controls.grid_btn.grid(row=0, column=5, padx=5, pady=10, sticky="ew")
    
    def export_button(self, header):
        btn_style = self.style_buttons()
        button = ctk.CTkButton(
            master=header,
            text="Exportar Gráficos",
            command=self._lidar_com_exportacao,
            **btn_style
        )
        button.grid(row=0, column=6, padx=5, pady=10, sticky="ew")
        return button

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

    def graphic_area(self):
        self.graph_container = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.graph_container.grid(row=1, column=0, sticky="nsew")
        self.graph_container.grid_rowconfigure(0, weight=1)
        self.graph_container.grid_columnconfigure(0, weight=1)

        gr = graphic.Graphic(self.graph_container)
        self.canvas = gr.canvas
        return gr


app = App()
app.mainloop()