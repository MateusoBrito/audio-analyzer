import customtkinter as ctk
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os
from datetime import datetime
from tkinter import messagebox

class RecordingDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        
        self.callback = callback # Função para chamar quando salvar
        self.recording = False
        self.audio_data = []
        self.fs = 44100 # Taxa de amostragem padrão
        self.stream = None

        # Configurações da Janela
        self.title("Gravar Áudio")
        self.geometry("350x250")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        self._build_ui()
        self.grab_set()

    def _build_ui(self):
        # Título / Status
        self.lbl_status = ctk.CTkLabel(self, text="Pronto para gravar", font=("Arial", 16, "bold"))
        self.lbl_status.pack(pady=(20, 10))

        self.lbl_timer = ctk.CTkLabel(self, text="00:00", font=("Arial", 30, "bold"), text_color="#8a9cfa")
        self.lbl_timer.pack(pady=10)

        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20, padx=20)

        self.btn_rec = ctk.CTkButton(
            btn_frame, text="● Gravar", command=self._toggle_recording,
            fg_color="#C75450", hover_color="#8a2e2b", width=140
        )
        self.btn_rec.pack(side="left", padx=5)

        self.btn_save = ctk.CTkButton(
            btn_frame, text="Salvar", command=self._save_recording,
            fg_color="#4A4D50", state="disabled", width=140
        )
        self.btn_save.pack(side="right", padx=5)

    def _toggle_recording(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        try:
            self.audio_data = [] # Limpa dados anteriores
            self.recording = True
            self.start_time = datetime.now()
            
            # Atualiza UI
            self.btn_rec.configure(text="■ Parar")
            self.btn_save.configure(state="disabled")
            self.lbl_status.configure(text="Gravando...", text_color="#C75450")

            # Inicia Stream de Áudio (Callback é executado em outra thread pelo SO)
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self._audio_callback)
            self.stream.start()

            # Inicia timer visual
            self._update_timer()

        except Exception as e:
            messagebox.showerror("Erro de Áudio", f"Não foi possível acessar o microfone.\n{e}")
            self.recording = False

    def _stop_recording(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        self.recording = False
        self.btn_rec.configure(text="● Gravar (Novo)")
        self.btn_save.configure(state="normal")
        self.lbl_status.configure(text="Gravação finalizada", text_color="white")

    def _audio_callback(self, indata, frames, time, status):
        """Chamado repetidamente pelo sounddevice enquanto grava"""
        if status:
            print(status)
        # Copia os dados do buffer para nossa lista
        self.audio_data.append(indata.copy())

    def _update_timer(self):
        """Atualiza o relógio na tela"""
        if self.recording:
            elapsed = datetime.now() - self.start_time
            # Formata mm:ss
            seconds = int(elapsed.total_seconds())
            time_str = f"{seconds//60:02d}:{seconds%60:02d}"
            self.lbl_timer.configure(text=time_str)
            # Agenda próxima atualização em 100ms
            self.after(100, self._update_timer)

    def _save_recording(self):
        if not self.audio_data:
            return

        # 1. Concatena os fragmentos de áudio num único array numpy
        recording = np.concatenate(self.audio_data, axis=0)

        # 2. Gera nome de arquivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gravacao_{timestamp}.wav"
        
        # 3. Cria pasta 'recordings' se não existir
        save_dir = "recordings"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        filepath = os.path.join(save_dir, filename)

        # 4. Salva o arquivo usando soundfile
        sf.write(filepath, recording, self.fs)
        
        # 5. Chama o callback passando o caminho completo
        self.callback(os.path.abspath(filepath))
        self.destroy()