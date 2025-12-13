import customtkinter as ctk
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
from datetime import datetime
from tkinter import messagebox

class RecordingDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.recording = False
        self.audio_data = [] # Lista de arrays numpy
        self.full_recording = None # Array numpy único (concatenado) para reprodução
        self.fs = 44100
        self.stream = None

        # Configurações da Janela
        self.title("Gravar Áudio")
        self.geometry("400x320") # Aumentei um pouco a altura
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        self._build_ui()
        
        # Foco
        self.after(10, lambda: self.grab_set())
        self.focus_force()

    def _build_ui(self):
        self.lbl_status = ctk.CTkLabel(self, text="Pronto para gravar", font=("Arial", 16, "bold"))
        self.lbl_status.pack(pady=(20, 10))

        self.lbl_timer = ctk.CTkLabel(self, text="00:00", font=("Arial", 30, "bold"), text_color="#8a9cfa")
        self.lbl_timer.pack(pady=10)

        # Botões de Controle
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20, padx=20)

        # Gravar / Parar
        self.btn_rec = ctk.CTkButton(
            btn_frame, text="● Gravar", command=self._toggle_recording,
            fg_color="#C75450", hover_color="#8a2e2b", width=100
        )
        self.btn_rec.pack(side="left", padx=5)

        # Ouvir (Novo)
        self.btn_play = ctk.CTkButton(
            btn_frame, text="▶ Ouvir", command=self._play_recording,
            fg_color="#3B8ED0", state="disabled", width=100
        )
        self.btn_play.pack(side="left", padx=5)

        # Salvar
        self.btn_save = ctk.CTkButton(
            btn_frame, text="Salvar", command=self._save_recording,
            fg_color="#4A4D50", state="disabled", width=100
        )
        self.btn_save.pack(side="right", padx=5)

    def _toggle_recording(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        try:
            # Reseta estado
            self.audio_data = [] 
            self.full_recording = None
            self.recording = True
            self.start_time = datetime.now()
            
            # UI
            self.btn_rec.configure(text="■ Parar")
            self.btn_save.configure(state="disabled")
            self.btn_play.configure(state="disabled")
            self.lbl_status.configure(text="Gravando...", text_color="#C75450")

            # Inicia Stream
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self._audio_callback)
            self.stream.start()

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
        
        # Concatena o áudio agora para ficar pronto para o Play
        if self.audio_data:
            self.full_recording = np.concatenate(self.audio_data, axis=0)
        
        # UI
        self.btn_rec.configure(text="● Gravar (Novo)")
        self.btn_save.configure(state="normal")
        
        # Habilita o botão Ouvir se tivermos dados
        if self.full_recording is not None and len(self.full_recording) > 0:
            self.btn_play.configure(state="normal")
            
        self.lbl_status.configure(text="Gravação finalizada", text_color="white")

    def _audio_callback(self, indata, frames, time, status):
        if status: print(status)
        self.audio_data.append(indata.copy())

    def _update_timer(self):
        if self.recording:
            elapsed = datetime.now() - self.start_time
            seconds = int(elapsed.total_seconds())
            time_str = f"{seconds//60:02d}:{seconds%60:02d}"
            self.lbl_timer.configure(text=time_str)
            self.after(100, self._update_timer)

    def _play_recording(self):
        """Reproduz o áudio gravado"""
        if self.full_recording is not None:
            self.lbl_status.configure(text="Reproduzindo...", text_color="#3B8ED0")
            # Toca o áudio de forma assíncrona (não trava a tela)
            sd.play(self.full_recording, self.fs)
            
            # (Opcional) Volta o texto depois que terminar
            duration_ms = int((len(self.full_recording) / self.fs) * 1000)
            self.after(duration_ms, lambda: self.lbl_status.configure(text="Pronto", text_color="white"))

    def _save_recording(self):
        if self.full_recording is None: return

        # Para o áudio se estiver tocando
        sd.stop()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gravacao_{timestamp}.wav"
        
        save_dir = "recordings"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        filepath = os.path.join(save_dir, filename)

        sf.write(filepath, self.full_recording, self.fs)
        
        self.callback(os.path.abspath(filepath))
        self.destroy()