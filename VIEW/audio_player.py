import customtkinter as ctk
import pygame
import wave


class AudioPlayer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#2b2b2b")

        pygame.mixer.init()
        self.current_audio = None
        self.audio_length = 0
        self.is_paused = False

        # --- Botões do player ---
        self.play_button = ctk.CTkButton(self, text="▶ Play", command=self.play_audio)
        self.play_button.pack(side="left", padx=10, pady=10)

        self.pause_button = ctk.CTkButton(self, text="⏸ Pause", command=self.pause_audio)
        self.pause_button.pack(side="left", padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self, text="⏹ Stop", command=self.stop_audio)
        self.stop_button.pack(side="left", padx=10, pady=10)

        # --- Slider de progresso ---
        self.progress_slider = ctk.CTkSlider(
            self, from_=0, to=100, number_of_steps=100, command=self.seek_audio
        )
        self.progress_slider.pack(fill="x", padx=10, pady=10, expand=True)

        self.update_progress()  # inicia loop de atualização

    # --- Funções principais ---
    def load_audio(self, file_path):
        """Carrega arquivo WAV para o player"""
        try:
            self.current_audio = file_path
            # calcula duração do áudio em segundos
            with wave.open(file_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                self.audio_length = frames / float(rate)

            self.progress_slider.configure(to=self.audio_length)
        except Exception as e:
            print(f"Erro ao carregar áudio no player: {e}")

    def play_audio(self):
        if self.current_audio:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.load(self.current_audio)
                pygame.mixer.music.play()

    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.progress_slider.set(0)

    def seek_audio(self, value):
        """Avança o áudio quando o usuário move o slider"""
        if self.current_audio:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_audio)
            pygame.mixer.music.play(start=float(value))

    def update_progress(self):
        """Atualiza a posição do slider a cada 200ms"""
        if pygame.mixer.music.get_busy():
            pos_ms = pygame.mixer.music.get_pos()  # posição em ms
            pos_sec = pos_ms / 1000.0
            if pos_sec <= self.audio_length:
                self.progress_slider.set(pos_sec)

        self.after(200, self.update_progress)
