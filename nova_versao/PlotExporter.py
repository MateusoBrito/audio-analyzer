import os
import matplotlib.pyplot as plt
from datetime import datetime

class PlotExporter:
    """
    Responsável por criar e salvar imagens dos gráficos em disco.
    """

    def save_plots(self, dir_path:str, plot_data_list:list, grid_enabled: bool):
        """
        Ponto de entrada principal. Salva os gráficos dos canais L e R.
        'plot_data_list' é uma lista de dicionários contendo os dados.
        """
        if not plot_data_list:
            raise ValueError("Nenhum dado de gráfico para exportar!")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save_channel(dir_path,timestamp,"esquerdo",plot_data_list,grid_enabled,'L')
        self._save_channel(dir_path,timestamp,"direito",plot_data_list,grid_enabled,'R')

        return [f"esquerdo_{timestamp}.png",
                f"direito_{timestamp}.png"]
    
    def _save_channel(self, dir_path, timestamp, nome_canal, 
                            plot_data_list, grid_enabled, data_key):
        """
        Lógica interna para criar e salvar a imagem de um único canal.
        'data_key' será 'L' ou 'R'.
        """

        fig,ax = plt.subplots(figsize=(10,5), dpi=300)
        for plot_data in plot_data_list:
            ax.plot(
                plot_data['freq'],
                plot_data[data_key],
                color=plot_data['color'],
                label=plot_data['label']
            )
        
        ax.grid(grid_enabled, which='both', linestyle=':', color='gray', alpha=0.5)
        ax.set_title(f"Canal {nome_canal.capitalize()}")
        ax.set_xlabel("Frequência (Hz)")
        ax.set_ylabel("Amplitude (normalizada)")
        ax.legend(fontsize=8, framealpha=0.5)

        nome_arquivo = f"{nome_canal}_{timestamp}.png"
        caminho_completo = os.path.join(dir_path,nome_arquivo)

        fig.savefig(caminho_completo, bbox_inches='tight', dpi=300)
        plt.close(fig)