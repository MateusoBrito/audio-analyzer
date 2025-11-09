import customtkinter as ctk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import serial.tools.list_ports
import time
import numpy as np
import pandas as pd
from datetime import datetime
import threading
import queue
import json

# Configuração do customtkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EMGApp:
    def __init__(self, root, active_channels: list, active_duration: int, active_baud: int):
        self.root = root
        self.root.title("Sistema de Aquisição EMG")
        self.root.geometry("1200x800")

        # Variáveis de controle
        self.connected = False
        self.recording = False
        self.test_running = False
        self.selected_channels = active_channels
        self.test_duration = active_duration
        self.serial_port = None
        self.data_queue = queue.Queue()
        self.baud = active_baud

        # Dados
        self.time_data = []
        self.channel_data = [[], [], []]
        self.max_points = 1000

        # Configuração da interface
        self.create_menu()
        self.create_connection_frame()
        self.create_control_frame()
        self.create_plot_frame()
        self.create_analysis_frame()

        # Thread para leitura serial
        self.serial_thread = None

    def create_menu(self):
        # "Gambiarra" porque o customtkinter não tem menu igual do Tk
        menu_frame = ctk.CTkFrame(self.root, height=40)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(menu_frame, text="Salvar Configurações", command=self.save_settings, width=140).pack(side="left", padx=5)
        ctk.CTkButton(menu_frame, text="Carregar Configurações", command=self.load_settings, width=140).pack(side="left", padx=5)
        ctk.CTkButton(menu_frame, text="Sobre", command=self.show_about, width=100).pack(side="left", padx=5)
        ctk.CTkButton(menu_frame, text="Sair", command=self.root.quit, width=100).pack(side="right", padx=5)

    def create_connection_frame(self):
        # Frame com título usando CTkFrame
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Título do frame
        ctk.CTkLabel(frame, text="Conexão Bluetooth", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=3, pady=5)

        # Portas COM disponíveis
        ctk.CTkLabel(frame, text="Porta COM:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.port_combobox = ctk.CTkComboBox(frame, width=150, values=[])
        self.port_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Botão para atualizar portas
        ctk.CTkButton(frame, text="Atualizar Portas", command=self.update_com_ports, width=120).grid(row=1, column=2, padx=5, pady=5)

        # Taxa de transmissão
        ctk.CTkLabel(frame, text="Baud Rate:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.baudrate_var = ctk.StringVar(value=str(self.baud))
        ctk.CTkComboBox(frame, variable=self.baudrate_var, values=["9600", "19200", "38400", "57600", "115200"], width=150).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Botão de conexão
        self.connect_button = ctk.CTkButton(frame, text="Conectar", command=self.toggle_connection, width=120)
        self.connect_button.grid(row=2, column=2, padx=5, pady=5)

        # Status da conexão
        self.connection_status = ctk.CTkLabel(frame, text="Desconectado", text_color="red", font=ctk.CTkFont(weight="bold"))
        self.connection_status.grid(row=3, column=0, columnspan=3, pady=10)

        # Atualizar portas COM disponíveis
        self.update_com_ports()

    def create_control_frame(self):
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Título
        ctk.CTkLabel(frame, text="Controle de Aquisição", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=4, pady=5)

        # Seleção de canais
        ctk.CTkLabel(frame, text="Canais Ativos:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.channel_vars = []
        self.channel_checkboxes = []
        for i in range(3):
            var = ctk.IntVar(value=1)
            self.channel_vars.append(var)
            cb = ctk.CTkCheckBox(frame, text=f"Canal {i+1}", variable=var, command=lambda idx=i: self.toggle_channel(idx))
            cb.grid(row=1, column=i+1, padx=5, pady=5, sticky="w")
            self.channel_checkboxes.append(cb)

        # Configuração de tempo
        ctk.CTkLabel(frame, text="Duração do Ensaio (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.duration_entry = ctk.CTkEntry(frame, width=150)
        self.duration_entry.insert(0, str(self.test_duration))
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Botões de controle
        self.start_button = ctk.CTkButton(frame, text="Iniciar Ensaio", command=self.start_test, state="disabled")
        self.start_button.grid(row=3, column=0, padx=5, pady=10)

        self.stop_button = ctk.CTkButton(frame, text="Parar Ensaio", command=self.stop_test, state="disabled")
        self.stop_button.grid(row=3, column=1, padx=5, pady=10)

        self.record_button = ctk.CTkButton(frame, text="Iniciar Gravação", command=self.toggle_recording, state="disabled")
        self.record_button.grid(row=3, column=2, padx=5, pady=10)

        # Status do ensaio
        self.test_status = ctk.CTkLabel(frame, text="Ensaio não iniciado", text_color="gray", font=ctk.CTkFont(weight="bold"))
        self.test_status.grid(row=4, column=0, columnspan=4, pady=10)

    def create_plot_frame(self):
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Configurar peso da linha para expansão
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Título
        ctk.CTkLabel(frame, text="Gráfico EMG em Tempo Real", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

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
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_analysis_frame(self):
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Título
        ctk.CTkLabel(frame, text="Análise de Dados", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=3, pady=5)

        # Tipo de análise
        ctk.CTkLabel(frame, text="Tipo de Análise:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.analysis_var = ctk.StringVar(value="Média")
        analysis_options = ["Média", "Valor de Pico", "RMS", "Integral", "Frequência Mediana"]
        self.analysis_combobox = ctk.CTkComboBox(frame, variable=self.analysis_var, values=analysis_options, state="readonly", width=200)
        self.analysis_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botão de análise
        ctk.CTkButton(frame, text="Realizar Análise", command=self.perform_analysis).grid(row=1, column=2, padx=5, pady=5)

        # Resultados
        ctk.CTkLabel(frame, text="Resultados:").grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.results_text = ctk.CTkTextbox(frame, height=100, width=600, state="disabled")
        self.results_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def update_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combobox.configure(values=ports)
        if ports:
            self.port_combobox.set(ports[0])

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
            self.connect_button.configure(text="Desconectar")
            self.connection_status.configure(text="Conectado", text_color="green")
            self.start_button.configure(state="normal")
            self.record_button.configure(state="normal")

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
        self.connect_button.configure(text="Conectar")
        self.connection_status.configure(text="Desconectado", text_color="red")
        self.start_button.configure(state="disabled")
        self.record_button.configure(state="disabled")

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
                            self.channel_data[i].append(0)
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
        self.test_status.configure(
            text=f"Ensaio em andamento - Tempo restante: {self.test_duration:.1f}s",
            text_color="green"
        )
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        # Iniciar contagem regressiva
        self.update_test_timer()

    def update_test_timer(self):
        if self.test_running:
            elapsed = time.time() - self.test_start_time
            remaining = max(0, self.test_duration - elapsed)
            self.test_status.configure(text=f"Ensaio em andamento - Tempo restante: {remaining:.1f}s")

            if remaining <= 0:
                self.stop_test()
            else:
                self.root.after(200, self.update_test_timer)

    def stop_test(self):
        self.test_running = False
        self.test_status.configure(text="Ensaio finalizado", text_color="blue")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def toggle_recording(self):
        if not self.recording:
            # Iniciar gravação
            self.recording = True
            self.record_button.configure(text="Parar Gravação")

            # Limpar dados anteriores
            self.time_data = []
            for i in range(3):
                self.channel_data[i] = []
        else:
            # Parar gravação e salvar dados
            self.recording = False
            self.record_button.configure(text="Iniciar Gravação")
            self.save_data()

    def save_data(self):
        if not self.time_data or not any(self.channel_data):
            messagebox.showwarning("Aviso", "Nenhum dado para salvar")
            return

        # Pedir informações para salvar
        save_dialog = ctk.CTkToplevel(self.root)
        save_dialog.title("Salvar Dados")
        save_dialog.geometry("450x250")

        # Nome do arquivo
        ctk.CTkLabel(save_dialog, text="Nome do Arquivo:").pack(pady=(10, 0))
        filename_entry = ctk.CTkEntry(save_dialog, width=350)
        default_filename = f"EMG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename_entry.insert(0, default_filename)
        filename_entry.pack(pady=5)

        # Diretório
        ctk.CTkLabel(save_dialog, text="Diretório:").pack(pady=(10, 0))
        dir_frame = ctk.CTkFrame(save_dialog)
        dir_frame.pack(pady=5)

        dir_entry = ctk.CTkEntry(dir_frame, width=280)
        dir_entry.pack(side="left", padx=5)

        def browse_dir():
            directory = filedialog.askdirectory()
            if directory:
                dir_entry.delete(0, "end")
                dir_entry.insert(0, directory)

        ctk.CTkButton(dir_frame, text="Procurar", command=browse_dir, width=60).pack(side="left")

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

        ctk.CTkButton(save_dialog, text="Salvar", command=do_save, width=150).pack(pady=20)

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
                # Implementação simplificada
                zero_crossings = np.where(np.diff(np.sign(data)))[0]
                if len(zero_crossings) > 1:
                    median_freq = 0.5 / np.median(np.diff(zero_crossings))
                    results += f"Canal {i+1}: Frequência Mediana ≈ {median_freq:.2f} Hz\n"
                else:
                    results += f"Canal {i+1}: Frequência Mediana não calculável\n"

        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.results_text.configure(state="disabled")

    def save_settings(self):
        settings = {
            "selected_port": self.port_combobox.get(),
            "selected_baud": self.baudrate_var.get(),
            "selected_channels": self.selected_channels,
            "selected_duration": self.duration_entry.get(),
        }

        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Sucesso", "Configurações salvas no arquivo settings.json")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar configurações:\n{str(e)}")

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)

            # Atualizar variáveis
            if "selected_baud" in settings:
                self.baudrate_var.set(settings["selected_baud"])
            if "selected_channels" in settings:
                self.selected_channels = settings["selected_channels"]
                for i in range(3):
                    self.channel_vars[i].set(self.selected_channels[i])
            if "selected_duration" in settings:
                self.duration_entry.delete(0, "end")
                self.duration_entry.insert(0, settings["selected_duration"])

            messagebox.showinfo("Sucesso", "Configurações carregadas do arquivo settings.json")
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo settings.json não encontrado")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar configurações:\n{str(e)}")

    def show_about(self):
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("Sobre")
        about_window.geometry("400x200")

        ctk.CTkLabel(about_window, text="Sistema de Aquisição EMG", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        ctk.CTkLabel(about_window, text="Versão 1.0").pack(pady=5)
        ctk.CTkLabel(about_window, text="Desenvolvido para Arduino UNO com 3 canais").pack(pady=5)
        ctk.CTkButton(about_window, text="Fechar", command=about_window.destroy, width=100).pack(pady=20)

def main():
    root = ctk.CTk()
    app = EMGApp(root, [1, 1, 1], 10, 115200)
    root.mainloop()

if __name__ == "__main__":
    main()
