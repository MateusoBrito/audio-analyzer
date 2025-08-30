import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from numpy.fft import fft, fftfreq
#import soundfile as sf
from datetime import datetime

class AudioAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise de Áudio - PPGMUSI/UFSJ")
        #self.root.iconbitmap('favicon.ico') 
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variáveis de estado
        self.current_file = None
        self.raw_data = None
        self.sample_rate = None
        self.plots = []
        self.grid_enabled = True  # Grade habilitada por padrão
        self.fft_scale = 1  # Fator de escala para amostragem FFT
        
        # Configuração da UI
        self.setup_ui()
        
        # Configura estilo dos gráficos
        plt.style.use('default') 
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles (TOP)
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(0,10))
        
        # Botões principais
        btn_style = {'width':15, 'bg':'#e1e1e1', 'relief':tk.GROOVE}
        tk.Button(control_frame, text="Carregar WAV", command=self.carregar_arquivo, **btn_style).pack(side=tk.LEFT, padx=5)
        self.btn_analisar = tk.Button(control_frame, text="Analisar", command=self.analisar_arquivo, state=tk.DISABLED, **btn_style)
        self.btn_analisar.pack(side=tk.LEFT, padx=5)
        
        # Checkbox para manter anterior
        self.keep_var = tk.IntVar()
        tk.Checkbutton(control_frame, text="Manter anterior", variable=self.keep_var, 
                     bg='#f0f0f0', command=self.toggle_keep_previous).pack(side=tk.LEFT, padx=20)
        
        # Controles de frequência
        freq_frame = tk.Frame(control_frame, bg='#f0f0f0')
        freq_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(freq_frame, text="Freq. Mín (Hz):", bg='#f0f0f0').grid(row=0, column=0, sticky='e')
        self.entry_fi = tk.Entry(freq_frame, width=8)
        self.entry_fi.insert(0, "20")
        self.entry_fi.grid(row=0, column=1, padx=5)
        
        tk.Label(freq_frame, text="Freq. Máx (Hz):", bg='#f0f0f0').grid(row=1, column=0, sticky='e')
        self.entry_fm = tk.Entry(freq_frame, width=8)
        self.entry_fm.insert(0, "20000")
        self.entry_fm.grid(row=1, column=1, padx=5)
        
        # Controle de amostragem FFT
        fft_frame = tk.Frame(control_frame, bg='#f0f0f0')
        fft_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(fft_frame, text="Amostragem FFT (x):", bg='#f0f0f0').grid(row=0, column=0, sticky='e')
        self.entry_fft_scale = tk.Entry(fft_frame, width=5)
        self.entry_fft_scale.insert(0, "1")
        self.entry_fft_scale.grid(row=0, column=1, padx=5)
        tk.Button(fft_frame, text="Aplicar", command=self.update_fft_scale, width=6).grid(row=0, column=2, padx=5)
        
        # Botão de grade
        self.grid_btn = tk.Button(control_frame, text="Grade: ON", command=self.toggle_grid, 
                                bg='#e1e1e1', relief=tk.SUNKEN, width=10)
        self.grid_btn.pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        action_frame = tk.Frame(control_frame, bg='#f0f0f0')
        action_frame.pack(side=tk.RIGHT)
        
        
        tk.Button(action_frame, text="Limpar Tudo", command=self.limpar_tudo, **btn_style).pack(side=tk.RIGHT, padx=5)
        tk.Button(action_frame, text="Exportar Gráficos", command=self.exportar_graficos, **btn_style).pack(side=tk.RIGHT, padx=5)
        
        # Área de gráficos
        graph_container = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, bd=1)
        graph_container.pack(fill=tk.BOTH, expand=True)
        
        self.fig, (self.ax_left, self.ax_right) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.subplots_adjust(wspace=0.3)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.reset_axes()
        
        # Console
        console_frame = tk.Frame(main_frame, bg='#f0f0f0')
        console_frame.pack(fill=tk.X, pady=(10,0))
        
        tk.Label(console_frame, text="Log de Operações:", bg='#f0f0f0').pack(anchor='w')
        self.console = scrolledtext.ScrolledText(console_frame, height=8, bg='white', fg='black')
        self.console.pack(fill=tk.X)
    
    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.grid_btn.config(text=f"Grade: {'ON' if self.grid_enabled else 'OFF'}",
                           relief=tk.SUNKEN if self.grid_enabled else tk.RAISED)
        # Força a atualização dos gráficos
        self.reset_axes(clear_plots=False)
        self.log(f"Grade dos gráficos: {'Ativada' if self.grid_enabled else 'Desativada'}")
    def update_fft_scale(self):
        try:
            new_scale = float(self.entry_fft_scale.get())
            if new_scale <= 0:
                raise ValueError("O valor deve ser maior que zero")
            self.fft_scale = new_scale
            self.log(f"Amostragem FFT ajustada para: {new_scale}x")
            if self.raw_data is not None:
                self.analisar_arquivo()
        except Exception as e:
            self.log(f"Erro ao ajustar amostragem FFT: {str(e)}", error=True)
            messagebox.showerror("Erro", str(e))
    
    def toggle_keep_previous(self):
        self.log(f"Manter plots anteriores: {'Ativado' if self.keep_var.get() else 'Desativado'}")
    
    def reset_axes(self, clear_plots=True):
        for ax in [self.ax_left, self.ax_right]:
            ax.clear()
            ax.set_facecolor('white')  # Fundo branco
            ax.set_xlabel("Frequência (Hz)", fontsize=10)
            ax.set_ylabel("Amplitude (normalizada)", fontsize=10)
            
            # Configuração completa da grade
            ax.grid(self.grid_enabled, which='both', linestyle=':', 
                   color='gray', alpha=0.5 if self.grid_enabled else 0.0)
        
        self.ax_left.set_title("Canal Esquerdo", fontsize=12, pad=10)
        self.ax_right.set_title("Canal Direito", fontsize=12, pad=10)
        
        if clear_plots:
            self.plots = []
        else:
            for plot_data in self.plots:
                freq, L, R, label, color = plot_data
                self.ax_left.plot(freq, L, color=color, label=label)
                self.ax_right.plot(freq, R, color=color, label=label)
        
        if self.plots:
            for ax in [self.ax_left, self.ax_right]:
                ax.legend(fontsize=8, framealpha=0.5)
        
        self.canvas.draw()
    
    def carregar_arquivo(self):
        arquivo = filedialog.askopenfilename(filetypes=[("Arquivos WAV", "*.wav")])
        if not arquivo:
            return
            
        try:
            #self.raw_data, self.sample_rate = sf.read(arquivo, dtype='float32')
            self.current_file = os.path.basename(arquivo)
            self.btn_analisar.config(state=tk.NORMAL)
            self.log(f"Arquivo carregado: {self.current_file}")
            self.analisar_arquivo()
            
        except Exception as e:
            self.log(f"Erro ao carregar: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Falha ao ler arquivo:\n{str(e)}")
    
    def analisar_arquivo(self):
        if self.raw_data is None:
            return
            
        try:
            fi = float(self.entry_fi.get())
            fm = float(self.entry_fm.get())
            
            if fi >= fm:
                raise ValueError("Frequência mínima deve ser menor que a máxima")
            
            self.reset_axes(clear_plots=not self.keep_var.get())
            
            freq, L, R = self.processar_audio(self.raw_data, self.sample_rate, fi, fm)
            color = f"C{len(self.plots)}"
            
            self.plots.append((freq, L, R, self.current_file, color))
            self.reset_axes(clear_plots=False)
            
            self.log(f"Análise concluída: {self.current_file} ({fi}-{fm}Hz)")
            
        except Exception as e:
            self.log(f"Erro na análise: {str(e)}", error=True)
            messagebox.showerror("Erro", str(e))
    
    def processar_audio(self, data, sample_rate, fi, fm):
        if data.ndim == 1:
            data = np.column_stack((data, data))
        
        n = len(data)
        # Aplica o fator de escala na amostragem
        step = int(self.fft_scale)
        if step < 1:
            step = 1
        
        freq = fftfreq(n, 1/sample_rate)[:n//2:step]
        
        L = np.abs(fft(data[:, 0]))[:n//2:step]
        R = np.abs(fft(data[:, 1]))[:n//2:step]
        
        mascara = (freq >= fi) & (freq <= fm)
        freq_filtrado = freq[mascara]
        
        L_norm = L[mascara] / (np.max(L[mascara]) or 1)
        R_norm = R[mascara] / (np.max(R[mascara]) or 1)
        
        return freq_filtrado, L_norm, R_norm
    
    def limpar_tudo(self):
        self.current_file = None
        self.raw_data = None
        self.sample_rate = None
        self.btn_analisar.config(state=tk.DISABLED)
        self.plots = []
        self.reset_axes()
        self.log("Sistema reiniciado")
    
    def exportar_graficos(self):
        if not self.plots:
            messagebox.showwarning("Aviso", "Nenhum gráfico para exportar!")
            return

        try:
            dir_path = filedialog.askdirectory(title="Selecione a pasta para salvar")
            if not dir_path:
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Canal Esquerdo
            fig, ax = plt.subplots(figsize=(8,4), dpi=300)
            for plot_data in self.plots:
                ax.plot(plot_data[0], plot_data[1], color=plot_data[4])
            ax.grid(self.grid_enabled, linestyle=':', alpha=0.5)
            ax.set_xlabel("Frequência (Hz)")
            ax.set_ylabel("Amplitude (normalizada)")
            fig.savefig(
                os.path.join(dir_path, f"esquerdo_{timestamp}.png"),
                bbox_inches='tight',
                pad_inches=0.1,
                dpi=300
            )
            plt.close(fig)
            
            # Canal Direito
            fig, ax = plt.subplots(figsize=(8,4), dpi=300)
            for plot_data in self.plots:
                ax.plot(plot_data[0], plot_data[2], color=plot_data[4])
            ax.grid(self.grid_enabled, linestyle=':', alpha=0.5)
            ax.set_xlabel("Frequência (Hz)")
            ax.set_ylabel("Amplitude (normalizada)")
            fig.savefig(
                os.path.join(dir_path, f"direito_{timestamp}.png"),
                bbox_inches='tight',
                pad_inches=0.1,
                dpi=300
            )
            plt.close(fig)
            
            self.log(f"Gráficos salvos em:\n{dir_path}")
            messagebox.showinfo("Sucesso", f"Gráficos exportados como:\n"
                                f"esquerdo_{timestamp}.png\n"
                                f"direito_{timestamp}.png")
            
        except Exception as e:
            self.log(f"Erro ao exportar: {str(e)}", error=True)
            messagebox.showerror("Erro", str(e))
    
    def log(self, message, error=False):
        tag = "[ERRO] " if error else "[INFO] "
        self.console.insert(tk.END, tag + message + "\n")
        self.console.see(tk.END)
        if error:
            self.console.tag_add("error", "end-2c linestart", "end-1c lineend")
            self.console.tag_config("error", foreground="red")

if __name__ == "__main__":
    plt.switch_backend('Agg')
    root = tk.Tk()
    app = AudioAnalyzerApp(root)
    root.mainloop()