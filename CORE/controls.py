import soundfile as sf
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from datetime import datetime


class Controls:
    def __init__(self, graphic):
        self.graphic = graphic
        self.current_file = None
        self.raw_data = None
        self.sample_rate = None
        self.plots = []
        self.fft_scale = 1  # Fator de escala FFT
        self.fi = 20
        self.fm = 20000

    def toggle_grid(self):
        self.graphic.grid_enabled = not self.graphic.grid_enabled

        # Atualiza apenas a grade, sem limpar os dados
        for ax in [self.graphic.ax_left, self.graphic.ax_right]:
            ax.grid(
                self.graphic.grid_enabled, 
                which="both", 
                linestyle=":", 
                color="gray", 
                alpha=0.5 if self.graphic.grid_enabled else 0.0
            )

        self.graphic.canvas.draw()
        print(f"Grade dos gráficos: {'Ativada' if self.graphic.grid_enabled else 'Desativada'}")


    def load_file(self, file_path):
        self.raw_data, self.sample_rate = sf.read(file_path, dtype="float32")
        self.file_name = os.path.basename(file_path)
        

    def processar_audio(self, data, sample_rate, fi, fm):
        if data.ndim == 1:
            data = np.column_stack((data, data))

        n = len(data)
        step = max(1, int(self.fft_scale))
        freq = fftfreq(n, 1/sample_rate)[:n//2:step]

        L = np.abs(fft(data[:, 0]))[:n//2:step]
        R = np.abs(fft(data[:, 1]))[:n//2:step]

        mascara = (freq >= fi) & (freq <= fm)
        freq_filtrado = freq[mascara]
        L_norm = L[mascara] / (np.max(L[mascara]) or 1)
        R_norm = R[mascara] / (np.max(R[mascara]) or 1)

        return freq_filtrado, L_norm, R_norm

    def analyze_audio(self):
        if self.raw_data is None or self.fi >= self.fm:
            return

        freq, L, R = self.processar_audio(self.raw_data, self.sample_rate, self.fi, self.fm)
        color = f"C{len(self.plots)}"
        self.plots.append((freq, L, R, self.file_name, color))

        # Atualiza o gráfico
        self.graphic.reset_axes()  # Limpa e redesenha
        for plot_data in self.plots:
            freq, L, R, label, color = plot_data
            self.graphic.ax_left.plot(freq, L, color=color, label=label)
            self.graphic.ax_right.plot(freq, R, color=color, label=label)
        for ax in [self.graphic.ax_left, self.graphic.ax_right]:
            ax.legend(fontsize=8, framealpha=0.5)
        self.graphic.canvas.draw()

    def update_fft_scale(self, new_scale):
        if new_scale <= 0:
            raise ValueError("O valor deve ser maior que zero")
        self.fft_scale = new_scale
        if self.raw_data is not None:
            self.analyze_audio()
    
    def exportar_graficos(self, dir_path: str):
        if not self.plots:
            # Em vez de um messagebox, levantamos um erro específico.
            raise ValueError("Nenhum gráfico para exportar!")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Executa a lógica de salvamento
        self._salvar_um_grafico(dir_path, timestamp, "esquerdo", 1)
        self._salvar_um_grafico(dir_path, timestamp, "direito", 2)
        
        # Retorna os nomes dos arquivos para a interface usar
        nomes_arquivos = [
            f"esquerdo_{timestamp}.png",
            f"direito_{timestamp}.png"
        ]
        return nomes_arquivos

    def _salvar_um_grafico(self, dir_path, timestamp, nome_canal, indice_dados):
        """
        Cria e salva a imagem de um único canal.
        """
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        
        for plot_data in self.plots:
            # Pega os dados de self.plots
            freq, _, _, label, color = plot_data
            dados_canal = plot_data[indice_dados]
            ax.plot(freq, dados_canal, color=color, label=label)
        
        # Acessa o objeto graphic para pegar o status da grade
        ax.grid(self.graphic.grid_enabled, which='both', linestyle=':', color='gray')
        ax.set_title(f"Canal {nome_canal.capitalize()}")
        ax.set_xlabel("Frequência (Hz)")
        ax.set_ylabel("Amplitude (normalizada)")
        ax.legend()
        
        nome_arquivo = f"{nome_canal}_{timestamp}.png"
        caminho_completo = os.path.join(dir_path, nome_arquivo)
        
        fig.savefig(caminho_completo, bbox_inches='tight', dpi=300)
        plt.close(fig)

    def limpar_tudo(self):
        self.current_file = None
        self.raw_data = None
        self.sample_rate = None
        #self.btn_analisar.config(state=ctk.DISABLED)
        self.plots = []
        self.graphic.reset_axes()
