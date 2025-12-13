from PIL import Image
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

class EMGAnalysisScreen(ctk.CTkFrame):
    def __init__(self, root, active_channels: list, active_duration: int, active_baud: int):
        self.root = root
        self.root.title("Sistema de Aquisição EMG")
        self.root.geometry("1600x900")

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
        self.channel_data = [[], []]
        self.max_points = 1000

        # Carregar ícones
        self.load_icons()

        self.root.grid_columnconfigure(0, weight=0)  # Sidebar esquerda
        self.root.grid_columnconfigure(1, weight=1)  # Área central
        self.root.grid_columnconfigure(2, weight=0)  # Sidebar direita
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_ui()

        # Thread para leitura serial
        self.serial_thread = None

    def load_icons(self):
        try:
            # Ícones da sidebar esquerda
            self.icon_settings = ctk.CTkImage(Image.open("images/settings.png"), size=(24, 24))
            self.icon_load = ctk.CTkImage(Image.open("images/upload.png"), size=(24, 24))
            self.icon_help = ctk.CTkImage(Image.open("images/about.png"), size=(24, 24))
            self.icon_menu = ctk.CTkImage(Image.open("images/home.png"), size=(24, 24))

            # Ícones da sidebar direita
            self.icon_save_ch1 = ctk.CTkImage(Image.open("images/export.png"), size=(24, 24))
            self.icon_save_ch2 = ctk.CTkImage(Image.open("images/export.png"), size=(24, 24))
            self.icon_save_both = ctk.CTkImage(Image.open("images/export.png"), size=(24, 24))

            # Outros ícones
            self.icon_bluetooth = ctk.CTkImage(Image.open('images/bluetooth.png'), size=(24, 24))
            self.icon_refresh = ctk.CTkImage(Image.open('images/refresh.png'), size=(24, 24))
            self.icon_connect = ctk.CTkImage(Image.open('images/connect.png'), size=(24, 24))
            self.icon_disconnect = ctk.CTkImage(Image.open('images/disconnect.png'), size=(24, 24))
            self.icon_record = ctk.CTkImage(Image.open('images/record.png'), size=(24, 24))
            self.icon_stop = ctk.CTkImage(Image.open('images/stop.png'), size=(24, 24))
            self.icon_analysis = ctk.CTkImage(Image.open('images/analysis.png'), size=(24, 24))
        except FileNotFoundError as e:
            # print(f"Erro ao carregar ícones: {e}")
            # messagebox.showerror("Erro de Ícone", f"Não foi possível encontrar um ícone: {e}")
            pass 

    def setup_ui(self):
        # A gambiarra pra ficar num estilo 'moderno' mas com as mesmas funcionalidades
        # Sidebar esquerda (Menu, negócios de salvar e etc.)
        self.sidebar_left = ctk.CTkFrame(self.root, fg_color="#1e1e1e", width=200, corner_radius=0)
        self.sidebar_left.grid(row=0, column=0, sticky="nswe")
        self.sidebar_left.pack_propagate(False)
        self.build_sidebar_left()

        # Área central (controles e gráficos em grid)
        self.central_container = ctk.CTkFrame(self.root, fg_color="#1a1a1a", corner_radius=0)
        self.central_container.grid(row=0, column=1, sticky="nsew")
        self.build_central_area()

        # Sidebar direita (Exportação)
        self.sidebar_right = ctk.CTkFrame(self.root, fg_color="#1e1e1e", width=220, corner_radius=0)
        self.sidebar_right.grid(row=0, column=2, sticky="nswe")
        self.sidebar_right.pack_propagate(False)
        self.build_sidebar_right()

    def build_sidebar_left(self):
        title_label = ctk.CTkLabel(
            self.sidebar_left,
            text="EMG System",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(20, 30), padx=10, anchor="center")

        # Botões da sidebar esquerda
        buttons_data = {
            " Salvar\nConfigurações": (self.icon_settings, self.save_settings),
            " Carregar\nConfigurações": (self.icon_load, self.load_settings),
            " Ajuda": (self.icon_help, self.show_about),
            " Menu": (self.icon_menu, lambda: messagebox.showinfo("Menu", "Voltar ao menu principal")),
        }

        # Esse botão de menu aqui é pra redirecionar pra tela inicial do programa geral

        for i, (text, (icon, cmd)) in enumerate(buttons_data.items()):
            btn = ctk.CTkButton(
                self.sidebar_left,
                text=text,
                command=cmd,
                image=icon,
                compound="left",
                anchor="w",
                fg_color="#2b2b2b",
                text_color="white",
                hover_color="#5e5e5e",
                height=50,
                corner_radius=10,
                font=ctk.CTkFont(size=15, weight="bold"),
            )
            btn.pack(fill="x", padx=15, pady=(15 if i == 0 else 10), anchor="n")

    def build_central_area(self):
        self.central_container.grid_rowconfigure(0, weight=1)  # Linha superior (conexão e canal 1)
        self.central_container.grid_rowconfigure(1, weight=1)  # Linha do meio (aquisição e canal 2)
        self.central_container.grid_rowconfigure(2, weight=0)  # Linha inferior (análise)
        self.central_container.grid_columnconfigure(0, weight=0, minsize=400)  # Coluna controles
        self.central_container.grid_columnconfigure(1, weight=1)  # Coluna gráficos

        self.connection_frame = ctk.CTkFrame(self.central_container, fg_color="#2b2b2b")
        self.connection_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.create_connection_controls()

        # Frame de controle de aquisição (linha 1, coluna 0)
        self.control_frame = ctk.CTkFrame(self.central_container, fg_color="#2b2b2b")
        self.control_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.create_acquisition_controls()

        # Frame para gráfico Canal 1 (linha 0, coluna 1)
        self.graph_frame_ch1 = ctk.CTkFrame(self.central_container, fg_color="#2b2b2b")
        self.graph_frame_ch1.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Frame para gráfico Canal 2 (linha 1, coluna 1)
        self.graph_frame_ch2 = ctk.CTkFrame(self.central_container, fg_color="#2b2b2b")
        self.graph_frame_ch2.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Criar gráficos
        self.create_plots()

        self.analysis_frame = ctk.CTkFrame(self.central_container, fg_color="#2b2b2b")
        self.analysis_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.create_analysis_controls()

    def create_connection_controls(self):
        # Título
        ctk.CTkLabel(
            self.connection_frame, 
            text="Conexão Bluetooth", 
            font=ctk.CTkFont(size=14, weight="bold"),
            image=self.icon_bluetooth,
            compound="left"
        ).grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")

        # Porta COM
        ctk.CTkLabel(self.connection_frame, text="Porta COM:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.port_combobox = ctk.CTkComboBox(self.connection_frame, width=120, values=[])
        self.port_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botão atualizar portas
        ctk.CTkButton(
            self.connection_frame, 
            text="Atualizar Portas", 
            command=self.update_com_ports, 
            width=40, 
            image=self.icon_refresh
        ).grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Baud Rate
        ctk.CTkLabel(self.connection_frame, text="Baud Rate:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.baudrate_var = ctk.StringVar(value=str(self.baud))
        ctk.CTkComboBox(
            self.connection_frame, 
            variable=self.baudrate_var, 
            values=["9600", "19200", "38400", "57600", "115200"], 
            width=120
        ).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Botão conectar
        self.connect_button = ctk.CTkButton(
            self.connection_frame, 
            text="Conectar", 
            command=self.toggle_connection, 
            width=100, 
            image=self.icon_connect,
        )
        self.connect_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Status
        self.connection_status = ctk.CTkLabel(
            self.connection_frame, 
            text="Desconectado", 
            text_color="red", 
            font=ctk.CTkFont(weight="bold")
        )
        self.connection_status.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Atualizar portas
        self.update_com_ports()

    def create_acquisition_controls(self):
        ctk.CTkLabel(
            self.control_frame, 
            text="Controle de Aquisição", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")

        # Canais ativos
        ctk.CTkLabel(self.control_frame, text="Canais Ativos:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.channel_vars = []
        self.channel_checkboxes = []
        for i in range(2):
            var = ctk.IntVar(value=1)
            self.channel_vars.append(var)
            cb = ctk.CTkCheckBox(
                self.control_frame, 
                text=f"Canal {i+1}", 
                variable=var, 
                command=lambda idx=i: self.toggle_channel(idx)
            )
            cb.grid(row=1, column=i+1, padx=5, pady=5, sticky="w")
            self.channel_checkboxes.append(cb)

        # Duração
        ctk.CTkLabel(self.control_frame, text="Duração (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.duration_entry = ctk.CTkEntry(self.control_frame, width=120)
        self.duration_entry.insert(0, str(self.test_duration))
        self.duration_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Botões de controle
        self.start_button = ctk.CTkButton(
            self.control_frame, 
            text="Iniciar Ensaio", 
            command=self.start_test, 
            state="disabled", 
            image=self.icon_record,
            fg_color="#2b2b2b",
            hover_color="#5e5e5e",
            width=150
        )
        self.start_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(
            self.control_frame, 
            text="Parar Ensaio", 
            command=self.stop_test, 
            state="disabled", 
            image=self.icon_stop,
            fg_color="#2b2b2b",
            hover_color="#5e5e5e",
            width=150
        )
        self.stop_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.record_button = ctk.CTkButton(
            self.control_frame, 
            text="Iniciar Gravação", 
            command=self.toggle_recording, 
            state="disabled",
            fg_color="#2b2b2b",
            hover_color="#5e5e5e",
            width=150
        )
        self.record_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Status
        self.test_status = ctk.CTkLabel(
            self.control_frame, 
            text="Ensaio não iniciado", 
            text_color="gray", 
            font=ctk.CTkFont(weight="bold")
        )
        self.test_status.grid(row=6, column=0, columnspan=3, pady=10)

    def create_plots(self):
        ctk.CTkLabel(
            self.graph_frame_ch1, 
            text="Canal 1 - Sinal EMG", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)

        self.fig_ch1, self.ax_ch1 = plt.subplots(figsize=(8, 3.5), dpi=100)
        self.fig_ch1.patch.set_facecolor("#2b2b2b")
        self.ax_ch1.set_facecolor("#1e1e1e")
        self.line_ch1, = self.ax_ch1.plot([], [], color="#00d4ff", linewidth=1.5, label="Canal 1")
        self.ax_ch1.set_xlabel("Tempo (s)", color="white")
        self.ax_ch1.set_ylabel("Amplitude (V)", color="white")
        self.ax_ch1.tick_params(colors="white")
        self.ax_ch1.grid(True, alpha=0.3)
        self.ax_ch1.legend(facecolor="#2b2b2b", edgecolor="white", labelcolor="white")

        self.canvas_ch1 = FigureCanvasTkAgg(self.fig_ch1, master=self.graph_frame_ch1)
        self.canvas_ch1.draw()
        self.canvas_ch1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Gráfico Canal 2
        ctk.CTkLabel(
            self.graph_frame_ch2, 
            text="Canal 2 - Sinal EMG", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)

        self.fig_ch2, self.ax_ch2 = plt.subplots(figsize=(8, 3.5), dpi=100)
        self.fig_ch2.patch.set_facecolor("#2b2b2b")
        self.ax_ch2.set_facecolor("#1e1e1e")
        self.line_ch2, = self.ax_ch2.plot([], [], color="#00ff88", linewidth=1.5, label="Canal 2")
        self.ax_ch2.set_xlabel("Tempo (s)", color="white")
        self.ax_ch2.set_ylabel("Amplitude (V)", color="white")
        self.ax_ch2.tick_params(colors="white")
        self.ax_ch2.grid(True, alpha=0.3)
        self.ax_ch2.legend(facecolor="#2b2b2b", edgecolor="white", labelcolor="white")

        self.canvas_ch2 = FigureCanvasTkAgg(self.fig_ch2, master=self.graph_frame_ch2)
        self.canvas_ch2.draw()
        self.canvas_ch2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_analysis_controls(self):
        ctk.CTkLabel(
            self.analysis_frame, 
            text="Análise de Dados", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")

        # Tipo de análise
        ctk.CTkLabel(self.analysis_frame, text="Tipo de Análise:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.analysis_var = ctk.StringVar(value="Média")
        analysis_options = ["Média", "Valor de Pico", "Mínimo"] #, "RMS", "Integral", "Frequência Mediana"]
        self.analysis_combobox = ctk.CTkComboBox(
            self.analysis_frame, 
            variable=self.analysis_var, 
            values=analysis_options, 
            state="readonly", 
            width=200
        )
        self.analysis_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botão análise
        ctk.CTkButton(
            self.analysis_frame, 
            text="Realizar Análise", 
            command=self.perform_analysis, 
            image=self.icon_analysis,
            fg_color="#2b2b2b",
            hover_color="#5e5e5e"
        ).grid(row=1, column=2, padx=5, pady=5)

        # Resultados
        ctk.CTkLabel(self.analysis_frame, text="Resultados:").grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.results_text = ctk.CTkTextbox(self.analysis_frame, height=80, width=600, state="disabled")
        self.results_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def build_sidebar_right(self):
        title_label = ctk.CTkLabel(
            self.sidebar_right,
            text="Exportar Gráficos",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(20, 30), padx=10, anchor="center")

        # Botões de exportação
        export_buttons = [
            (" Salvar Gráfico\nCanal 1", self.save_graph_ch1, self.icon_save_ch1),
            (" Salvar Gráfico\nCanal 2", self.save_graph_ch2, self.icon_save_ch2),
            (" Salvar Ambos", self.save_both_graphs, self.icon_save_both),
        ]

        for i, (text, cmd, icon) in enumerate(export_buttons):
            btn = ctk.CTkButton(
                self.sidebar_right,
                text=text,
                command=cmd,
                image=icon,
                compound="left",
                anchor="w",
                fg_color="#2b2b2b",
                text_color="white",
                hover_color="#5e5e5e",
                height=50,
                corner_radius=10,
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            btn.pack(fill="x", padx=15, pady=10, anchor="n")

    def save_graph_ch1(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=f"EMG_Canal1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            if file_path:
                self.fig_ch1.savefig(file_path, dpi=300, bbox_inches="tight", facecolor="#2b2b2b")
                messagebox.showinfo("Sucesso", f"Gráfico do Canal 1 salvo em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar gráfico:\n{str(e)}")

    def save_graph_ch2(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=f"EMG_Canal2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            if file_path:
                self.fig_ch2.savefig(file_path, dpi=300, bbox_inches="tight", facecolor="#2b2b2b")
                messagebox.showinfo("Sucesso", f"Gráfico do Canal 2 salvo em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar gráfico:\n{str(e)}")

    def save_both_graphs(self):
        try:
            dir_path = filedialog.askdirectory(title="Selecione a pasta para salvar os gráficos")
            if dir_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file1 = f"{dir_path}/EMG_Canal1_{timestamp}.png"
                file2 = f"{dir_path}/EMG_Canal2_{timestamp}.png"

                self.fig_ch1.savefig(file1, dpi=300, bbox_inches="tight", facecolor="#2b2b2b")
                self.fig_ch2.savefig(file2, dpi=300, bbox_inches="tight", facecolor="#2b2b2b")

                messagebox.showinfo("Sucesso", f"Gráficos salvos em:\n{file1}\n{file2}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar gráficos:\n{str(e)}")

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
            self.connect_button.configure(text="Desconectar", image=self.icon_disconnect)
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
        self.connect_button.configure(text="Conectar", image=self.icon_connect)
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
            # Esperado: "CH1:val1,CH2:val2"
            parts = data.split(',')
            values = []
            for part in parts:
                if ':' in part:
                    val_str = part.split(':')[1]
                    values.append(float(val_str))

            if len(values) >= 2:
                timestamp = time.time()
                self.data_queue.put((timestamp, values))

                # Atualizar gráfico se o teste estiver rodando
                if self.test_running:
                    self.update_plot(timestamp, values)

                # Se gravando, armazenar dados
                if self.recording:
                    self.time_data.append(timestamp)
                    for i in range(2):
                        if self.selected_channels[i]:
                            self.channel_data[i].append(values[i])
                        else:
                            self.channel_data[i].append(0)
        except Exception as e:
            print(f"Erro ao processar dados: {e}")

    def update_plot(self, timestamp, values):
        if self.selected_channels[0]:
            x_data_ch1 = list(self.line_ch1.get_xdata())
            y_data_ch1 = list(self.line_ch1.get_ydata())
            x_data_ch1.append(timestamp - self.test_start_time)
            y_data_ch1.append(values[0])

            if len(x_data_ch1) > self.max_points:
                x_data_ch1 = x_data_ch1[-self.max_points:]
                y_data_ch1 = y_data_ch1[-self.max_points:]

            self.line_ch1.set_data(x_data_ch1, y_data_ch1)
            self.ax_ch1.relim()
            self.ax_ch1.autoscale_view()
            self.canvas_ch1.draw()

        # Atualizar Canal 2
        if self.selected_channels[1]:
            x_data_ch2 = list(self.line_ch2.get_xdata())
            y_data_ch2 = list(self.line_ch2.get_ydata())
            x_data_ch2.append(timestamp - self.test_start_time)
            y_data_ch2.append(values[1])

            if len(x_data_ch2) > self.max_points:
                x_data_ch2 = x_data_ch2[-self.max_points:]
                y_data_ch2 = y_data_ch2[-self.max_points:]

            self.line_ch2.set_data(x_data_ch2, y_data_ch2)
            self.ax_ch2.relim()
            self.ax_ch2.autoscale_view()
            self.canvas_ch2.draw()

    def toggle_channel(self, channel_idx):
        self.selected_channels[channel_idx] = self.channel_vars[channel_idx].get()

        # Mostrar/ocultar linha no gráfico
        if channel_idx == 0:
            self.line_ch1.set_visible(self.selected_channels[0])
            self.canvas_ch1.draw()
        elif channel_idx == 1:
            self.line_ch2.set_visible(self.selected_channels[1])
            self.canvas_ch2.draw()

    # ========== Funções de Controle de Teste ==========

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
        for i in range(2):
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
            self.record_button.configure(text="Parar gravação")

            # Limpar dados anteriores
            self.time_data = []
            for i in range(2):
                self.channel_data[i] = []
        else:
            # Parar gravação e salvar dados
            self.recording = False
            self.record_button.configure(text="Iniciar gravação")
            self.save_data()

    def save_data(self):
        if not self.time_data or not any(self.channel_data):
            messagebox.showwarning("Aviso", "Nenhum dado para salvar")
            return

        # Dialog para salvar
        save_dialog = ctk.CTkToplevel(self.root)
        save_dialog.title("Salvar dados")
        save_dialog.geometry("450x250")

        # Nome do arquivo
        ctk.CTkLabel(save_dialog, text="Nome do arquivo:").pack(pady=(10, 0))
        filename_entry = ctk.CTkEntry(save_dialog, width=350)
        default_filename = f"EMG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename_entry.insert(0, default_filename)
        filename_entry.pack(pady=5)

        ctk.CTkLabel(save_dialog, text="Pasta:").pack(pady=(10, 0))
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
                messagebox.showerror("Erro", "Selecione uma pasta")
                return

            full_path = f"{directory}/{filename}"

            try:
                # Criar DataFrame com os dados
                data_dict = {'Tempo (s)': [t - self.time_data[0] for t in self.time_data]}
                for i in range(2):
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

        for i in range(2):
            if not self.selected_channels[i] or not self.channel_data[i]:
                continue

            data = self.channel_data[i]

            if analysis_type == "Média":
                value = np.mean(data)
                results += f"Canal {i+1}: Média = {value:.4f} V\n"

            elif analysis_type == "Valor de Pico":
                value = np.max(np.abs(data))
                results += f"Canal {i+1}: Valor de Pico = {value:.4f} V\n"

            elif analysis_type == "Mínimo":
                value = np.min(np.abs(data))
                results += f"Canal {i+1}: Mínimo = {value:.4f} V\n"
            #
            # elif analysis_type == "RMS":
            #     value = np.sqrt(np.mean(np.square(data)))
            #     results += f"Canal {i+1}: RMS = {value:.4f} V\n"
            #
            # elif analysis_type == "Integral":
            #     dt = np.diff([t - self.time_data[0] for t in self.time_data])
            #     integral = np.sum(data[:-1] * dt)
            #     results += f"Canal {i+1}: Integral = {integral:.4f} V·s\n"
            #
            # elif analysis_type == "Frequência Mediana":
            #     # Implementação simplificada
            #     zero_crossings = np.where(np.diff(np.sign(data)))[0]
            #     if len(zero_crossings) > 1:
            #         median_freq = 0.5 / np.median(np.diff(zero_crossings))
            #         results += f"Canal {i+1}: Frequência Mediana ≈ {median_freq:.2f} Hz\n"
            #     else:
            #         results += f"Canal {i+1}: Frequência Mediana não calculável\n"
            #
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
                for i in range(2):
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
        about_window.title("Ajuda")
        about_window.geometry("500x300")

        ctk.CTkLabel(
            about_window, 
            text="Sistema de Aquisição EMG", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        help_text = """
        Versão 2.0

        Desenvolvido para Arduino com 2 canais EMG

        Instruções:
        1. Conecte o dispositivo Bluetooth
        2. Selecione a porta COM e configure o Baud Rate
        3. Clique em "Conectar"
        4. Configure os canais ativos e duração do ensaio
        5. Clique em "Iniciar Ensaio" para começar
        6. Use os botões da direita para salvar os gráficos
        """

        ctk.CTkLabel(
            about_window, 
            text=help_text,
            justify="left"
        ).pack(pady=10, padx=20)

        ctk.CTkButton(
            about_window, 
            text="Fechar", 
            command=about_window.destroy, 
            width=100
        ).pack(pady=20)


def main():
    root = ctk.CTk()
    def on_close():
        ans = messagebox.askokcancel("Sair", "Deseja encerrar o programa?")
        if ans:
            root.destroy()
    app = EMGApp(root, [1, 1], 10, 115200)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
