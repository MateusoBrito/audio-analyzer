import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import sys
import subprocess
import re

class ArduinoConnectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conexão Arduino - Serial/Bluetooth")
        self.serial_connection = None
        
        # Interface
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface gráfica"""
        self.frame = ttk.Frame(self.root, padding="20")
        self.frame.pack(expand=True, fill='both')
        
        ttk.Label(self.frame, text="Seletor de Conexão Arduino", font=('Arial', 14)).pack(pady=10)
        
        # Botão para portas disponíveis
        self.btn_portas = ttk.Button(self.frame, text="Listar Portas Disponíveis", 
                                   command=self.mostrar_menu_portas)
        self.btn_portas.pack(pady=15)
        
        # Status da conexão
        self.status_frame = ttk.Frame(self.frame)
        self.status_frame.pack(pady=10)
        
        ttk.Label(self.status_frame, text="Status:").pack(side='left')
        self.lbl_status = ttk.Label(self.status_frame, text="Desconectado", foreground="red")
        self.lbl_status.pack(side='left', padx=5)
        
        # Botão de desconectar
        self.btn_disconnect = ttk.Button(self.frame, text="Desconectar", 
                                        state='disabled', command=self.desconectar)
        self.btn_disconnect.pack(pady=5)
        
        # Monitor de conexão
        self.verificar_conexao()
    
    def listar_portas_disponiveis(self):
        """Lista todas as portas disponíveis (Serial e Bluetooth)"""
        portas = []
        
        # 1. Portas Seriais (USB)
        for porta in serial.tools.list_ports.comports():
            # Identifica Arduinos por descrição comum
            descricao = porta.description.lower()
            is_arduino = ('arduino' in descricao or 
                         'ch340' in descricao or  # Common CH340 chip
                         'cp210' in descricao)    # Common CP210x chip
            tipo = "Arduino USB" if is_arduino else descricao
            portas.append(("SERIAL", porta.device, tipo))
        
        # 2. Portas Bluetooth (Linux - rfcomm)
        if sys.platform == 'linux':
            try:
                resultado = subprocess.run(['rfcomm'], capture_output=True, text=True)
                for linha in resultado.stdout.split('\n'):
                    if 'rfcomm' in linha:
                        match = re.search(r'rfcomm(\d+):.*([0-9A-F:]{17})', linha)
                        if match:
                            portas.append(("BLUETOOTH", f"/dev/rfcomm{match.group(1)}", 
                                         f"BT Device {match.group(2)}"))
            except:
                pass
        
        return portas
    
    def mostrar_menu_portas(self):
        """Mostra menu pop-up com portas disponíveis"""
        menu_portas = tk.Menu(self.root, tearoff=0)
        portas = self.listar_portas_disponiveis()
        
        if not portas:
            menu_portas.add_command(label="Nenhuma porta encontrada", state="disabled")
        else:
            for tipo, porta, descricao in portas:
                menu_portas.add_command(
                    label=f"{'[USB]' if tipo == 'SERIAL' else '[BT]'} {porta} - {descricao}",
                    command=lambda p=porta, t=tipo: self.conectar(p, t)
                )
        
        # Mostrar menu abaixo do botão
        x = self.btn_portas.winfo_rootx()
        y = self.btn_portas.winfo_rooty() + self.btn_portas.winfo_height()
        try:
            menu_portas.tk_popup(x, y)
        finally:
            menu_portas.grab_release()
    
    def conectar(self, porta, tipo):
        """Estabelece conexão com a porta selecionada"""
        try:
            if tipo == "SERIAL":
                # Conexão Serial (USB)
                self.serial_connection = serial.Serial(porta, 9600, timeout=1)
                self.lbl_status.config(text=f"Conectado: {porta}", foreground="green")
                messagebox.showinfo("Conexão", f"Conectado via USB\nPorta: {porta}")
                
            elif tipo == "BLUETOOTH":
                # Conexão Bluetooth (Linux rfcomm)
                self.lbl_status.config(text=f"Conectado: {porta}", foreground="green")
                messagebox.showinfo("Conexão", 
                    f"Conectado via Bluetooth\nPorta: {porta}\n\n"
                    "Nota: Para comunicação, use esta porta como serial.")
            
            self.btn_disconnect.config(state='enabled')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na conexão:\n{str(e)}")
            self.lbl_status.config(text="Erro na conexão", foreground="red")
    
    def desconectar(self):
        """Fecha a conexão atual"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.serial_connection = None
        self.lbl_status.config(text="Desconectado", foreground="red")
        self.btn_disconnect.config(state='disabled')
        messagebox.showinfo("Info", "Desconectado com sucesso")
    
    def verificar_conexao(self):
        """Atualiza o status da conexão periodicamente"""
        if self.serial_connection and self.serial_connection.is_open:
            self.lbl_status.config(foreground="green")
        else:
            self.lbl_status.config(foreground="red")
        self.root.after(1000, self.verificar_conexao)

# Inicialização
if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoConnectionApp(root)
    root.mainloop()