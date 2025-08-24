import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# 3. Agora importar pyplot e outros módulos gráficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Restante das importações...
import serial
import serial.tools.list_ports
import time
import numpy as np
import pandas as pd
from datetime import datetime
import threading
import queue


class EMGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Aquisição EMG")
        self.root.geometry("1200x800")
        
        # Variáveis de controle
        self.connected = False
        self.recording = False
        self.test_running = False
        self.selected_channels = [1, 1, 1]  # Todos ativos por padrão
        self.test_duration = 10  # Duração padrão em segundos
        self.serial_port = None
        self.data_queue = queue.Queue()
        
        # Dados
        self.time_data = []
        self.channel_data = [[], [], []]
        self.max_points = 1000  # Número máximo de pontos no gráfico
        
        # Configuração da interface
        self.create_menu()
        self.create_connection_frame()
        self.create_control_frame()
        self.create_plot_frame()
        self.create_analysis_frame()
        
        # Thread para leitura serial
        self.serial_thread = None
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salvar Configurações", command=self.save_settings)
        file_menu.add_command(label="Carregar Configurações", command=self.load_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_connection_frame(self):
        frame = ttk.LabelFrame(self.root, text="Conexão Bluetooth", padding=10)
        frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Portas COM disponíveis
        ttk.Label(frame, text="Porta COM:").grid(row=0, column=0, sticky="w")
        self.port_combobox = ttk.Combobox(frame, width=15)
        self.port_combobox.grid(row=0, column=1, padx=5)
        
        # Botão para atualizar portas
        ttk.Button(frame, text="Atualizar Portas", command=self.update_com_ports).grid(row=0, column=2, padx=5)
        
        # Taxa de transmissão
        ttk.Label(frame, text="Baud Rate:").grid(row=1, column=0, sticky="w")
        self.baudrate_var = tk.StringVar(value="115200")
        ttk.Combobox(frame, textvariable=self.baudrate_var, 
                    values=["9600", "19200", "38400", "57600", "115200"], width=10).grid(row=1, column=1, padx=5, sticky="w")
        
        # Botão de conexão
        self.connect_button = ttk.Button(frame, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(row=1, column=2, padx=5)
        
        # Status da conexão
        self.connection_status = ttk.Label(frame, text="Desconectado", foreground="red")
        self.connection_status.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Atualizar portas COM disponíveis
        self.update_com_ports()
    
    def create_control_frame(self):
        frame = ttk.LabelFrame(self.root, text="Controle de Aquisição", padding=10)
        frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Seleção de canais
        ttk.Label(frame, text="Canais Ativos:").grid(row=0, column=0, sticky="w")
        self.channel_vars = []
        for i in range(3):
            var = tk.IntVar(value=1)
            self.channel_vars.append(var)
            cb = ttk.Checkbutton(frame, text=f"Canal {i+1}", variable=var, 
                                command=lambda i=i: self.toggle_channel(i))
            cb.grid(row=0, column=i+1, padx=5, sticky="w")
        
        # Configuração de tempo
        ttk.Label(frame, text="Duração do Ensaio (s):").grid(row=1, column=0, sticky="w")
        self.duration_entry = ttk.Entry(frame, width=10)
        self.duration_entry.insert(0, "10")
        self.duration_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Botões de controle
        self.start_button = ttk.Button(frame, text="Iniciar Ensaio", command=self.start_test, state=tk.DISABLED)
        self.start_button.grid(row=2, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(frame, text="Parar Ensaio", command=self.stop_test, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=5, pady=5)
        
        self.record_button = ttk.Button(frame, text="Iniciar Gravação", command=self.toggle_recording, state=tk.DISABLED)
        self.record_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Status do ensaio
        self.test_status = ttk.Label(frame, text="Ensaio não iniciado", foreground="gray")
        self.test_status.grid(row=3, column=0, columnspan=3, pady=5)
    
    def create_plot_frame(self):
        frame = ttk.LabelFrame(self.root, text="Gráfico EMG em Tempo Real", padding=10)
        frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")
        
        # Configurar peso da linha para expansão
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Criar figura do matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.fig.subplots_adjust(bottom=0.15)
        self.lines = []
        colors = ['blue', 'green', 'red']
        
        for i in range(3):
            line, = self.ax.plot([], [], color=colors[i], label=f'Canal {i+1}')
            self.lines.append(line)
        
        self.ax.set_xlabel('Tempo (s)')
        self.ax.set_ylabel('Amplitude (V)')
        self.ax.set_title('Sinais EMG')
        self.ax.legend()
        self.ax.grid(True)
        
        # Canvas para o gráfico
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_analysis_frame(self):
        frame = ttk.LabelFrame(self.root, text="Análise de Dados", padding=10)
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Tipo de análise
        ttk.Label(frame, text="Tipo de Análise:").grid(row=0, column=0, sticky="w")
        self.analysis_var = tk.StringVar()
        analysis_options = ["Média", "Valor de Pico", "RMS", "Integral", "Frequência Mediana"]
        self.analysis_combobox = ttk.Combobox(frame, textvariable=self.analysis_var, 
                                             values=analysis_options, state="readonly")
        self.analysis_combobox.current(0)
        self.analysis_combobox.grid(row=0, column=1, padx=5, sticky="w")
        
        # Botão de análise
        ttk.Button(frame, text="Realizar Análise", command=self.perform_analysis).grid(row=0, column=2, padx=5)
        
        # Resultados
        ttk.Label(frame, text="Resultados:").grid(row=1, column=0, sticky="w")
        self.results_text = tk.Text(frame, height=5, width=60, state=tk.DISABLED)
        self.results_text.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=2, column=3, sticky="ns")
        self.results_text.config(yscrollcommand=scrollbar.set)
    
    def update_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combobox['values'] = ports
        if ports:
            self.port_combobox.current(0)
    
    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        port = self.port_combobox.get()
        baudrate = self.baudrate_var.get()
        
        if not port:
            messagebox.showerror("Erro", "Selecione uma porta COM válida")
            return
        
        try:
            self.serial_port = serial.Serial(port, int(baudrate), timeout=1)
            self.connected = True
            self.connect_button.config(text="Desconectar")
            self.connection_status.config(text="Conectado", foreground="green")
            self.start_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL)
            
            # Iniciar thread de leitura serial
            self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.serial_thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar:\n{str(e)}")
    
    def disconnect(self):
        if self.recording:
            self.toggle_recording()
        
        if self.test_running:
            self.stop_test()
        
        self.connected = False
        self.connect_button.config(text="Conectar")
        self.connection_status.config(text="Desconectado", foreground="red")
        self.start_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.DISABLED)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
    
    def read_serial_data(self):
        while self.connected and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        self.process_serial_data(line)
            except:
                break
    
    def process_serial_data(self, data):
        try:
            # Esperado: "CH1:val1,CH2:val2,CH3:val3"
            parts = data.split(',')
            values = []
            
            for part in parts:
                if ':' in part:
                    val_str = part.split(':')[1]
                    values.append(float(val_str))
            
            if len(values) == 3:
                timestamp = time.time()
                self.data_queue.put((timestamp, values))
                
                # Atualizar gráfico se o teste estiver rodando
                if self.test_running:
                    self.update_plot(timestamp, values)
                    
                    # Se gravando, armazenar dados
                    if self.recording:
                        self.time_data.append(timestamp)
                        for i in range(3):
                            if self.selected_channels[i]:
                                self.channel_data[i].append(values[i])
                            else:
                                self.channel_data[i].append(0)  # Preencher com zero se canal desativado
        except Exception as e:
            print(f"Erro ao processar dados: {e}")
    
    def update_plot(self, timestamp, values):
        # Atualizar dados das linhas
        for i in range(3):
            if self.selected_channels[i]:
                x_data = list(self.lines[i].get_xdata())
                y_data = list(self.lines[i].get_ydata())
                
                x_data.append(timestamp - self.test_start_time)
                y_data.append(values[i])
                
                # Manter apenas os últimos pontos
                if len(x_data) > self.max_points:
                    x_data = x_data[-self.max_points:]
                    y_data = y_data[-self.max_points:]
                
                self.lines[i].set_data(x_data, y_data)
        
        # Ajustar limites do gráfico
        if len(self.lines[0].get_xdata()) > 0:
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
    
    def toggle_channel(self, channel_idx):
        self.selected_channels[channel_idx] = self.channel_vars[channel_idx].get()
        
        # Mostrar/ocultar linha no gráfico
        self.lines[channel_idx].set_visible(self.selected_channels[channel_idx])
        self.ax.legend()
        self.canvas.draw()
    
    def start_test(self):
        try:
            self.test_duration = float(self.duration_entry.get())
            if self.test_duration <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Digite uma duração válida em segundos")
            return
        
        # Limpar dados anteriores
        self.time_data = []
        for i in range(3):
            self.channel_data[i] = []
        
        self.test_running = True
        self.test_start_time = time.time()
        self.test_status.config(text=f"Ensaio em andamento - Tempo restante: {self.test_duration:.1f}s", foreground="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Iniciar contagem regressiva
        self.update_test_timer()
    
    def update_test_timer(self):
        if self.test_running:
            elapsed = time.time() - self.test_start_time
            remaining = max(0, self.test_duration - elapsed)
            self.test_status.config(text=f"Ensaio em andamento - Tempo restante: {remaining:.1f}s")
            
            if remaining <= 0:
                self.stop_test()
            else:
                self.root.after(200, self.update_test_timer)
    
    def stop_test(self):
        self.test_running = False
        self.test_status.config(text="Ensaio finalizado", foreground="blue")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def toggle_recording(self):
        if not self.recording:
            # Iniciar gravação
            self.recording = True
            self.record_button.config(text="Parar Gravação")
            
            # Limpar dados anteriores
            self.time_data = []
            for i in range(3):
                self.channel_data[i] = []
        else:
            # Parar gravação e salvar dados
            self.recording = False
            self.record_button.config(text="Iniciar Gravação")
            self.save_data()
    
    def save_data(self):
        if not self.time_data or not any(self.channel_data):
            messagebox.showwarning("Aviso", "Nenhum dado para salvar")
            return
        
        # Pedir informações para salvar
        save_dialog = tk.Toplevel(self.root)
        save_dialog.title("Salvar Dados")
        save_dialog.geometry("400x300")
        
        # Nome do arquivo
        ttk.Label(save_dialog, text="Nome do Arquivo:").pack(pady=(10,0))
        filename_entry = ttk.Entry(save_dialog, width=30)
        default_filename = f"EMG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename_entry.insert(0, default_filename)
        filename_entry.pack(pady=5)
        
        # Diretório
        ttk.Label(save_dialog, text="Diretório:").pack(pady=(10,0))
        dir_frame = ttk.Frame(save_dialog)
        dir_frame.pack(pady=5)
        
        dir_entry = ttk.Entry(dir_frame, width=30)
        dir_entry.pack(side=tk.LEFT, padx=5)
        
        def browse_dir():
            directory = filedialog.askdirectory()
            if directory:
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, directory)
        
        ttk.Button(dir_frame, text="Procurar", command=browse_dir).pack(side=tk.LEFT)
        
        # Botão de salvar
        def do_save():
            filename = filename_entry.get()
            directory = dir_entry.get()
            
            if not filename:
                messagebox.showerror("Erro", "Digite um nome de arquivo")
                return
            
            if not directory:
                messagebox.showerror("Erro", "Selecione um diretório")
                return
            
            full_path = f"{directory}/{filename}"
            
            try:
                # Criar DataFrame com os dados
                data_dict = {'Tempo (s)': [t - self.time_data[0] for t in self.time_data]}
                for i in range(3):
                    if self.selected_channels[i]:
                        data_dict[f'Canal_{i+1}'] = self.channel_data[i]
                
                df = pd.DataFrame(data_dict)
                df.to_csv(full_path, index=False)
                
                messagebox.showinfo("Sucesso", f"Dados salvos em:\n{full_path}")
                save_dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar arquivo:\n{str(e)}")
        
        ttk.Button(save_dialog, text="Salvar", command=do_save).pack(pady=20)
    
    def perform_analysis(self):
        if not self.time_data or not any(self.channel_data):
            messagebox.showwarning("Aviso", "Nenhum dado para análise")
            return
        
        analysis_type = self.analysis_var.get()
        results = ""
        
        for i in range(3):
            if not self.selected_channels[i] or not self.channel_data[i]:
                continue
            
            data = self.channel_data[i]
            
            if analysis_type == "Média":
                value = np.mean(data)
                results += f"Canal {i+1}: Média = {value:.2f} V\n"
            elif analysis_type == "Valor de Pico":
                value = np.max(np.abs(data))
                results += f"Canal {i+1}: Valor de Pico = {value:.2f} V\n"
            elif analysis_type == "RMS":
                value = np.sqrt(np.mean(np.square(data)))
                results += f"Canal {i+1}: RMS = {value:.2f} V\n"
            elif analysis_type == "Integral":
                dt = np.diff([t - self.time_data[0] for t in self.time_data])
                integral = np.sum(data[:-1] * dt)
                results += f"Canal {i+1}: Integral = {integral:.2f} V·s\n"
            elif analysis_type == "Frequência Mediana":
                # Implementação simplificada - EMG real precisaria de FFT
                zero_crossings = np.where(np.diff(np.sign(data)))[0]
                if len(zero_crossings) > 1:
                    median_freq = 0.5 / np.median(np.diff(zero_crossings))
                    results += f"Canal {i+1}: Frequência Mediana ≈ {median_freq:.2f} Hz\n"
                else:
                    results += f"Canal {i+1}: Frequência Mediana não calculável\n"
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, results)
        self.results_text.config(state=tk.DISABLED)
    
    def save_settings(self):
        # Implementar salvar configurações em arquivo
        pass
    
    def load_settings(self):
        # Implementar carregar configurações de arquivo
        pass
    
    def show_about(self):
        messagebox.showinfo("Sobre", "Sistema de Aquisição EMG\nVersão 1.0\n\nDesenvolvido para Arduino UNO com 3 canais")

def main():
    root = tk.Tk()
    app = EMGApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()