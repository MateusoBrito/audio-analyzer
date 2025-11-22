import soundfile as sf
import os
import librosa
import numpy as np
from AudioAnalyzer import AudioAnalyzer
from PlotFrames import (FFTPlotFrame, 
                        WaveformPlotFrame, 
                        RMSPlotFrame, 
                        SpectrogramPlotFrame, 
                        HilbertPlotFrame, 
                        BasePlotFrame,
                        DashboardFrame)
from PlotExporter import PlotExporter

class AppController:
    def __init__(self, ui_plot_container):
        self.analyzer = AudioAnalyzer()
        self.exporter = PlotExporter()

        self.plot_container = ui_plot_container # O CTkFrame que segura o ggráfico
        self.active_plot_frame = None # O gráfico atual (FFTPlotFrame, etc)

        self.loaded_files = {} # Dicionário para guardar {filename: (y,sr)}
        self.active_filename = None
        
        self.plot_list = [] # Lista de {filename, color}
        
        self.grid_enabled = True
        self.fi = 20
        self.fm = 20000
        self.fft_scale = 1

        self.analysis_type = "Dashboard"

    def load_file(self, file_path):
        """
        Carrega um arquivo de áudio e armazena seus dados e informações básicas.

        Parâmetros:
            file_path (str): Caminho completo do arquivo de áudio a ser carregado.
        """

        y, sr = librosa.load(file_path, sr=None, mono=False)
        filename = os.path.basename(file_path)

        # Se não for estéreo duplica o mono
        if y.ndim ==1:
            y = np.column_stack((y,y)) 
        elif y.shape[0] == 2: # Librosa carrega (2,N)
            y = y.T # Transpor para (N,2)
        
        self.loaded_files[filename] = (y,sr)
        self.active_filename = filename

    def set_analysis_type(self, type_name):
        """Chamado na UI"""
        if self.analysis_type == type_name and self.active_plot_frame:
             return # Evita recriar se for o mesmo
             
        self.analysis_type = type_name

        # Destrói o frame do gráfico antigo
        if self.active_plot_frame:
            self.active_plot_frame.destroy()
        
        # Cria o novo Frame de gráfico
        if type_name == "Dashboard":
            self.active_plot_frame = DashboardFrame(self.plot_container)
        elif type_name == "FFT":
            self.active_plot_frame = FFTPlotFrame(self.plot_container)
        elif type_name == "Waveform":
            self.active_plot_frame = WaveformPlotFrame(self.plot_container)
        elif type_name == "RMS":
            self.active_plot_frame = RMSPlotFrame(self.plot_container)
        elif type_name == "Spectrogram":
            self.active_plot_frame = SpectrogramPlotFrame(self.plot_container)
        elif type_name == "Hilbert":
            self.active_plot_frame = HilbertPlotFrame(self.plot_container)
        else:
            self.active_plot_frame = BasePlotFrame(self.plot_container)

        # --- ESTA LINHA É OBRIGATÓRIA PARA O GRÁFICO APARECER ---
        self.active_plot_frame.pack(fill="both", expand=True)
        
        # Chama o desenho inicial (caso já tenha arquivos carregados)
        self.draw_plots()

    def draw_plots(self):
        """
        Função MESTRA de desenho.
        Verifica o tipo de análise atual e o estado da lista de plots,
        solicita os dados ao Modelo e atualiza a Visão.
        """
        # Validação básica: se não tem frame de plot ou arquivos, não faz nada
        if not self.active_plot_frame: return
        
        filename_to_plot = self.active_filename
        if not filename_to_plot and self.plot_list:
            filename_to_plot = self.plot_list[0]['filename']
        
        if not filename_to_plot or filename_to_plot not in self.loaded_files:
            self.active_plot_frame.clear()
            self.active_plot_frame.draw()
            return

        # Pega os dados crus
        y, sr = self.loaded_files[filename_to_plot]

        if self.analysis_type == "Dashboard":
            # 3. Atualiza FFT (Reusa a lógica de lista de plots)
            fft_frame = self.active_plot_frame.get_frame('FFT')
            fft_frame.reset_axes(self.grid_enabled)
            
            # 1. Atualiza Waveform
            times, y_data = self.analyzer.get_waveform_data(y, sr)
            self.active_plot_frame.get_frame('Waveform').plot(times, y_data, sr)
            
            # 2. Atualiza Spectrogram
            S_db = self.analyzer.get_spectrogram_data(y, sr)
            self.active_plot_frame.get_frame('Spectrogram').plot(S_db, sr)

            # 3. RMS (Faltava isso!)
            times_rms, rms_data = self.analyzer.get_rms_data(y, sr)
            self.active_plot_frame.get_frame('RMS').plot(times_rms, rms_data)
            
            # 4. Hilbert (Faltava isso!)
            samples, env_data = self.analyzer.get_hilbert_data(y)
            self.active_plot_frame.get_frame('Hilbert').plot(samples, env_data)
            
            
            # Desenha todos os arquivos carregados no FFT do dashboard
            for plot_item in self.plot_list:
                if plot_item['filename'] not in self.loaded_files: continue
                y_fft, sr_fft = self.loaded_files[plot_item['filename']]
                
                freq, L, R = self.analyzer.get_fft_data(
                    y_fft, sr_fft, self.fi, self.fm, self.fft_scale
                )
                fft_frame.add_plot(freq, L, R, plot_item['filename'], plot_item['color'])
            
            fft_frame.draw()
            return # Fim da lógica Dashboard
        
        # ---------------------------------------------------------
        # CENÁRIO 1: FFT (Suporta múltiplos gráficos sobrepostos)
        # ---------------------------------------------------------
        if self.analysis_type == "FFT":
            print("Entrei FFT")
            # Verifica se o frame atual suporta adição de plots (segurança)
            if not hasattr(self.active_plot_frame, 'add_plot'):
                return

            # 1. Limpa os eixos para redesenhar do zero
            self.active_plot_frame.reset_axes(self.grid_enabled)

            # 2. Itera sobre a lista de estado 'plot_list'
            for plot_item in self.plot_list:
                filename = plot_item['filename']
                color = plot_item['color']

                # Se o arquivo foi removido da memória, ignora
                if filename not in self.loaded_files:
                    continue
                
                y, sr = self.loaded_files[filename]

                # Pede dados ao Modelo
                freq, L, R = self.analyzer.get_fft_data(
                    y, sr, self.fi, self.fm, self.fft_scale
                )

                # Manda a Visão adicionar a linha
                self.active_plot_frame.add_plot(freq, L, R, filename, color)
            
            # 3. Finaliza o desenho no Canvas
            self.active_plot_frame.draw()
            return

        # ---------------------------------------------------------
        # CENÁRIO 2: Gráficos de Arquivo Único (Waveform, RMS, etc.)
        # ---------------------------------------------------------

        # Roteamento para o tipo específico
        if self.analysis_type == "Waveform":
            times, y_data = self.analyzer.get_waveform_data(y, sr)
            self.active_plot_frame.plot(times, y_data,sr)
            
        elif self.analysis_type == "RMS":
            times, rms_data = self.analyzer.get_rms_data(y, sr)
            self.active_plot_frame.plot(times, rms_data)

        elif self.analysis_type == "Spectrogram":
            S_db = self.analyzer.get_spectrogram_data(y, sr)
            self.active_plot_frame.plot(S_db, sr)
            
        elif self.analysis_type == "Hilbert":
            samples, env_data = self.analyzer.get_hilbert_data(y)
            self.active_plot_frame.plot(samples, env_data)

        # O método .plot() dessas classes já deve chamar self.draw(), 
        # mas se não chamar, você pode descomentar a linha abaixo:
        # self.active_plot_frame.draw()

    def add_active_file_to_plot(self):
        """
        Chamado pelo botão 'Analisar'.
        Adiciona o arquivo atualmente selecionado à lista de plots e redesenha.
        """
        if self.active_filename is None:
            print("Nenhum arquivo selecionado.")
            return

        # Define uma cor nova baseada na quantidade de plots
        color = f"C{len(self.plot_list)}"
        
        # Atualiza o ESTADO
        self.plot_list.append({
            'filename': self.active_filename,
            'color': color
        })
        
        self.draw_plots()
    
    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.draw_plots()
    
    def update_analysis_params(self, fi=None, fm=None, fft_scale=None):
        """(Refatorado de 'update_fft_scale' e lógica de fi/fm)"""
        if fi is not None: self.fi=fi
        if fm is not None: self.fm=fm
        if fft_scale is not None: self.fft_scale=fft_scale

        if self.plot_list:
            self.draw_plots()
    
    def clean(self):
        """limpar_tudo"""
        self.loaded_files = {}
        self.active_filename = None
        self.plot_list = []
        self.draw_plots()
    
    def export_graph(self, dir_path:str):
        """exportar_graficos"""
        if not self.plot_list:
            raise ValueError("Nenhum gráfico para exportar!")
        
        plot_data_list = []
        for plot_item in self.plot_list:
            filename = plot_item['filename']
            y,sr = self.loaded_files[filename]

            freq,L,R = self.analyzer.get_fft_data(
                y,sr,self.fi,self.fm, self.fft_scale
            )

            plot_data_list.append({
            'freq': freq, 'L': L, 'R': R,
            'label': filename,
            'color': plot_item['color']
            })
        
        try:
            nomes_arquivos = self.exporter.save_plots(
                dir_path,
                plot_data_list,
                self.grid_enabled
            )
            return nomes_arquivos
        except Exception as e:
            raise ValueError(f"Erro ao exportar: {e}")
            raise e


