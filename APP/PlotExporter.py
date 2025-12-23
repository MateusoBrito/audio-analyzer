import os
import matplotlib.pyplot as plt
import librosa.display
import numpy as np
from datetime import datetime

class PlotExporter:
    """
    Responsável por criar e salvar imagens de TODOS os gráficos em disco.
    """

    def save_dashboard(self, dir_path: str, 
                       active_audio: tuple, 
                       plot_list: list, 
                       analyzer, 
                       grid_enabled: bool,
                       params: dict):
        """
        Salva o conjunto completo de gráficos.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []

        # Desempacota o áudio ativo
        if active_audio:
            y, sr = active_audio
            # Garante que usamos apenas um canal para análises temporais
            y_mono = y[:, 0] if y.ndim > 1 else y

            # 1. Salvar Forma de Onda
            saved_files.append(self._save_waveform(dir_path, timestamp, y_mono, sr, analyzer, grid_enabled))
            
            # 2. Salvar Espectrograma
            saved_files.append(self._save_spectrogram(dir_path, timestamp, y_mono, sr, analyzer))
            
            # 3. Salvar RMS
            saved_files.append(self._save_rms(dir_path, timestamp, y_mono, sr, analyzer, grid_enabled))
            
            # 4. Salvar Hilbert
            saved_files.append(self._save_hilbert(dir_path, timestamp, y_mono, analyzer, grid_enabled))

        # 5. Salvar FFT (Comparativo - usa plot_list)
        if plot_list:
            files_fft = self._save_fft_comparison(dir_path, timestamp, plot_list, grid_enabled)
            saved_files.extend(files_fft)

        return saved_files

    def _create_figure(self):
        """Helper para criar figura padrão de exportação (fundo branco para impressão)"""
        return plt.subplots(figsize=(15, 5), dpi=300)

    def _save_waveform(self, dir_path, ts, y, sr, analyzer, grid):
        fig, ax = self._create_figure()
        
        times, y_data = analyzer.get_waveform_data(y, sr)
        librosa.display.waveshow(y_data, sr=sr, ax=ax, color='steelblue')
        
        ax.set_title("Forma de Onda")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(grid, linestyle=':', alpha=0.5)
        
        fname = f"waveform_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_spectrogram(self, dir_path, ts, y, sr, analyzer):
        fig, ax = self._create_figure()
        
        S_db = analyzer.get_spectrogram_data(y, sr)
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', ax=ax, cmap='magma')
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        
        ax.set_title("Espectrograma")
        
        fname = f"spectrogram_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_rms(self, dir_path, ts, y, sr, analyzer, grid):
        fig, ax = self._create_figure()
        
        times, rms = analyzer.get_rms_data(y, sr)
        ax.plot(times, rms, color='orange')
        
        ax.set_title("Envelope RMS")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude RMS")
        ax.grid(grid, linestyle=':', alpha=0.5)
        
        fname = f"rms_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_hilbert(self, dir_path, ts, y, analyzer, grid):
        fig, ax = self._create_figure()
        
        samples, env = analyzer.get_hilbert_data(y)
        ax.plot(samples, env, color='purple')
        
        ax.set_title("Envelope Hilbert")
        ax.set_xlabel("Amostras")
        ax.set_ylabel("Amplitude")
        ax.grid(grid, linestyle=':', alpha=0.5)
        
        fname = f"hilbert_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_fft_comparison(self, dir_path, ts, plot_list, grid):
        """Salva o FFT Mono (Comparativo)"""
        saved = []
        
        # Cria apenas UMA figura (Mono)
        fig, ax = self._create_figure()
        
        for plot_data in plot_list:
            # Agora usamos 'mag' e 'freq'
            ax.plot(
                plot_data['freq'], 
                plot_data['mag'], 
                color=plot_data['color'], 
                label=plot_data['label']
            )
        
        ax.set_title(f"FFT - Comparativo (Mono)")
        ax.set_xlabel("Frequência (Hz)")
        ax.set_ylabel("Magnitude")
        ax.legend(fontsize=8)
        ax.grid(grid, linestyle=':', alpha=0.5)
        
        fname = f"fft_comparison_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        saved.append(fname)
            
        return saved