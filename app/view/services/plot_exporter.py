import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Configurações de Estilo para Artigos (Fundo Branco)
EXPORT_FACECOLOR = 'white'
TEXT_COLOR = 'black'

class PlotExporter:
    """
    Exporta apenas os gráficos ativos no Dashboard, mantendo as cores das linhas.
    """

    def save_dashboard(self, dir_path: str, 
                       active_audio: tuple, 
                       plot_list: list, 
                       analyzer, 
                       grid_enabled: bool,
                       params: dict,
                       active_charts: list): 
        """
        Salva gráficos baseados na lista 'active_charts'.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []

        # Desempacota áudio
        if active_audio:
            x, fs = active_audio
            if x.ndim > 1: x = np.mean(x, axis=1) # Garante Mono

            fi = params.get('fi', 20)
            fm = params.get('fm', 20000)

            # --- GERAÇÃO CONDICIONAL ---
            
            # 1. Waveform (Azul Claro)
            if "Waveform" in active_charts:
                saved_files.append(self._save_waveform(dir_path, timestamp, x, fs, analyzer, grid_enabled))
            
            # 2. Espectrograma (Colorido)
            if "Spectrogram" in active_charts:
                saved_files.append(self._save_spectrogram(dir_path, timestamp, x, fs, analyzer, fi, fm))
            
            # 3. Pitch / Frequência Instantânea (Verde)
            if "Pitch" in active_charts or "HilbertFreq" in active_charts:
                saved_files.append(self._save_pitch_hilbert(dir_path, timestamp, x, fs, analyzer, grid_enabled))

            # --- [NEW] 3.5 Variação de Pitch STFT (Azul) ---
            if "PitchSTFT" in active_charts:
                saved_files.append(self._save_pitch_stft(dir_path, timestamp, x, fs, analyzer, grid_enabled))
            
            # 4. Envoltória Hilbert (Vermelho Tracejado)
            if "Hilbert" in active_charts or "HilbertEnvelope" in active_charts:
                saved_files.append(self._save_envelope_hilbert(dir_path, timestamp, x, fs, analyzer, grid_enabled))
            
            # 5. RMS (Laranja)
            if "RMS" in active_charts:
                saved_files.append(self._save_rms(dir_path, timestamp, x, fs, analyzer, grid_enabled))
            
            # 6. SFFT 3D (Opcional)
            if "SFFT3D" in active_charts:
                saved_files.append(self._save_sfft_3d(dir_path, timestamp, x, fs, analyzer, fi, fm))

        # 7. FFT Comparativo
        if plot_list and ("FFT" in active_charts):
            files_fft = self._save_fft_comparison(dir_path, timestamp, plot_list, grid_enabled)
            saved_files.extend(files_fft)

        return saved_files

    def _create_figure(self, is_3d=False):
        """Cria figura com fundo branco para publicação."""
        if is_3d:
            fig = plt.figure(figsize=(10, 6), dpi=150)
            ax = fig.add_subplot(111, projection='3d')
        else:
            fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
        
        # Força fundo branco
        fig.patch.set_facecolor(EXPORT_FACECOLOR)
        
        if not is_3d:
            ax.set_facecolor(EXPORT_FACECOLOR)
            # Textos e bordas em preto
            ax.tick_params(colors=TEXT_COLOR, labelcolor=TEXT_COLOR)
            for spine in ax.spines.values():
                spine.set_edgecolor(TEXT_COLOR)
            ax.xaxis.label.set_color(TEXT_COLOR)
            ax.yaxis.label.set_color(TEXT_COLOR)
            ax.title.set_color(TEXT_COLOR)
            
        return fig, ax

    def _save_waveform(self, dir_path, ts, x, fs, analyzer, grid):
        fig, ax = self._create_figure()
        t, y = analyzer.get_waveform_data(x, fs)
        ax.plot(t, y, color='#4FC3F7', linewidth=0.8)
        ax.set_title("Forma de Onda")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(grid, linestyle=':', alpha=0.5, color='gray')
        fname = f"waveform_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_spectrogram(self, dir_path, ts, x, fs, analyzer, fi, fm):
        fig, ax = self._create_figure()
        t, f, S_db = analyzer.calcular_espectrograma(x, fs, fmin=fi, fmax=fm)
        img = ax.pcolormesh(t, f, S_db, shading='gouraud', cmap='inferno')
        cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TEXT_COLOR)
        ax.set_title("Espectrograma")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Frequência (Hz)")
        fname = f"spectrogram_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_pitch_hilbert(self, dir_path, ts, x, fs, analyzer, grid):
        fig, ax = self._create_figure()
        t, f_inst = analyzer.get_instantaneous_frequency(x, fs)
        
        # AJUSTE 1: Cor igual ao Dashboard (Azul #448AFF em vez de Verde)
        ax.plot(t, f_inst, color='#448AFF', linewidth=1.2, label="F0 (Hz)")
        
        # AJUSTE 2: Título igual ao Dashboard
        ax.set_title("Frequência Instantânea (Pitch)") 
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Frequência (Hz)")
        
        # AJUSTE 3: Escala Dinâmica (Igual ao Dashboard)
        # Removemos o ax.set_ylim(0, 22000) fixo
        if len(f_inst) > 0:
            max_f0 = np.max(f_inst)
            if max_f0 > 0:
                ax.set_ylim(0, max_f0 * 1.2)
        
        ax.grid(grid, linestyle=':', alpha=0.5, color='gray')
        
        fname = f"pitch_hilbert_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    # --- [NEW] MÉTODO NOVO ---
    def _save_pitch_stft(self, dir_path, ts, x, fs, analyzer, grid):
        fig, ax = self._create_figure()
        # Chama o novo método do analyzer
        t, f_stft = analyzer.get_pitch_variation_stft(x, fs)
        
        # Cor Azul (#448AFF) igual à definida na View
        ax.plot(t, f_stft, color='#448AFF', linewidth=1.5)
        
        ax.set_title("Variação da Afinação (Pitch via STFT)")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Frequência (Hz)")
        ax.grid(grid, linestyle=':', alpha=0.5, color='gray')
        
        fname = f"pitch_stft_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname
    # -------------------------

    def _save_envelope_hilbert(self, dir_path, ts, x, fs, analyzer, grid):
        fig, ax = self._create_figure()
        t, env = analyzer.get_hilbert_envelope(x, fs)
        ax.plot(t, env, color='red', linestyle='--', label='Envoltória', linewidth=1.0)
        ax.set_title("Envoltória de Hilbert")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(grid, linestyle=':', alpha=0.5, color='gray')
        ax.legend()
        fname = f"envelope_hilbert_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_rms(self, dir_path, ts, x, fs, analyzer, grid):
        fig, ax = self._create_figure()
        t, rms = analyzer.get_rms_data(x, fs)
        ax.plot(t, rms, color='orange', linewidth=1.0)
        ax.set_title("Envelope RMS")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(grid, linestyle=':', alpha=0.5, color='gray')
        fname = f"rms_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_sfft_3d(self, dir_path, ts, x, fs, analyzer, fi, fm):
        fig, ax = self._create_figure(is_3d=True)
        T, Fgrid, Zxx_mag = analyzer.get_sfft_3d_data(x, fs, fmin=fi, fmax=fm)
        ax.plot_surface(
            T, Fgrid, Zxx_mag, 
            cmap='viridis', edgecolor='none', 
            rstride=8, cstride=8, antialiased=False
        )
        ax.set_title("Espectro 3D (SFFT)")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Freq (Hz)")
        ax.set_zlabel("dB")
        ax.view_init(elev=30, azim=-60)
        fname = f"sfft_3d_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        return fname

    def _save_fft_comparison(self, dir_path, ts, plot_list, grid):
        saved = []
        fig, ax = self._create_figure()
        for plot_data in plot_list:
            ax.plot(
                plot_data['freq'], plot_data['mag'], 
                color=plot_data['color'], 
                label=plot_data['label'],
                linewidth=1.2
            )
        ax.set_title(f"FFT Comparativo")
        ax.set_xlabel("Frequência (Hz)")
        ax.set_ylabel("Magnitude")
        ax.legend(fontsize=8)
        ax.grid(grid, linestyle=':', alpha=0.5, color='gray')
        fname = f"fft_comparison_{ts}.png"
        fig.savefig(os.path.join(dir_path, fname), bbox_inches='tight')
        plt.close(fig)
        saved.append(fname)
        return saved