import customtkinter as ctk
from PIL import Image
from CORE import controls, graphic
from tkinter import filedialog, messagebox, ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sounder Analyzer")
        self.geometry("900x500")
        self.config(bg='#f0f0f0')

        # Configure grid da janela principal
        self.grid_rowconfigure(1, weight=1)  # área do gráfico cresce
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_ui()

    def setup_ui(self):
        self.graphic = self.graphic_area()
        self.controls = controls.Controls(self.graphic)
        self.header_area()

    def header_area(self):
        self.header = ctk.CTkFrame(self, width=900, height=50, fg_color="#F4F4F4", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

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
        

    def upload_button(self, header):
        btn_style = {"width": 120, "height": 30, "fg_color": "#e1e1e1",
                     "text_color": "black", "hover_color": "#d1d1d1", "corner_radius": 5}
        btn = ctk.CTkButton(header, text="Carregar WAV", command=self.upload_window, **btn_style)
        btn.grid(row=0, column=1, padx=5, pady=10)
        return btn
    
    def analyze_audio(self):
        try:
            self.controls.analyze_audio()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao analisar áudio: {str(e)}")

    def analyze_button(self, header):
        btn_style = {"width": 120, "height": 30, "fg_color": "#e1e1e1",
                     "text_color": "black", "hover_color": "#d1d1d1", "corner_radius": 5}
        btn = ctk.CTkButton(header, text="Analisar", command=self.analyze_audio, state=ctk.DISABLED,**btn_style)
        btn.grid(row=0, column=2, padx=5, pady=10)
        return btn
    
    def frequency_buttons(self, header):
        # Controles de frequência
        freq_frame = ctk.CTkFrame(header, fg_color='#f0f0f0')
        freq_frame.grid(row=0, column=3, padx=20, pady=5, sticky="w")
        
        ctk.CTkLabel(freq_frame, text="Freq. Mín (Hz):",text_color="black").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        btn_entry_fi = ctk.CTkEntry(freq_frame, width=80, fg_color="#c2c2c2")
        btn_entry_fi.insert(0, "20")
        btn_entry_fi.grid(row=0, column=1, padx=5, pady=2)

        ctk.CTkLabel(freq_frame, text="Freq. Máx (Hz):",text_color="black").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        btn_entry_fm = ctk.CTkEntry(freq_frame, width=80, fg_color="#2b2b2b"  )
        btn_entry_fm.insert(0, "20000")
        btn_entry_fm.grid(row=1, column=1, padx=5, pady=2)

        try:
            fi_value = float(btn_entry_fi.get())
            fm_value = float(btn_entry_fm.get())
            self.controls.fi = fi_value
            self.controls.fm = fm_value
        except ValueError:
            messagebox.showerror("Erro", "Valores de frequência inválidos. Usando valores padrão (20Hz - 20000Hz).")
            
    def graphic_area(self):
        self.graph_container = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.graph_container.grid(row=1, column=0, sticky="nsew")
        gr = graphic.Graphic(self.graph_container)
        self.canvas = gr.canvas
        return gr

app = App()
app.mainloop()
