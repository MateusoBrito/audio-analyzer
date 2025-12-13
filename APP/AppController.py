import os
import librosa
import numpy as np
from AudioAnalyzer import AudioAnalyzer
# Importamos apenas o Dashboard, pois ele gerencia os outros internamente
from PlotFrames import DashboardFrame
from PlotExporter import PlotExporter

class AppController:
    def __init__(self, ui_plot_container):
        self.analyzer = AudioAnalyzer()
        self.exporter = PlotExporter()

        self.plot_container = ui_plot_container 
        self.active_plot_frame = None 

        self.loaded_files = {} 
        self.active_filename = None
        self.plot_list = [] 
        
        self.grid_enabled = True
        self.fi = 20
        self.fm = 20000
        self.fft_scale = 1

    def load_file(self, file_path):
        """Carrega áudio e armazena na memória."""
        try:
            y, sr = librosa.load(file_path, sr=None, mono=False)
            filename = os.path.basename(file_path)

            if y.ndim == 1:
                y = np.column_stack((y, y)) 
            elif y.shape[0] == 2: 
                y = y.T 
            
            self.loaded_files[filename] = (y, sr)
            self.active_filename = filename
            print(f"Arquivo carregado: {filename}")
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")

    def set_analysis_type(self, type_name="Dashboard"):
        """
        Inicializa a visualização.
        Nota: O argumento type_name é ignorado, sempre força Dashboard.
        """
        # Se já existe um frame, destrói para recriar limpo
        if self.active_plot_frame:
            self.active_plot_frame.destroy()
        
        # Cria e exibe SEMPRE o DashboardFrame
        self.active_plot_frame = DashboardFrame(self.plot_container)
        self.active_plot_frame.pack(fill="both", expand=True)
        
        # Desenha se já houver dados
        self.draw_plots()

    def draw_plots(self):
        """
        Função MESTRA simplificada: Calcula e desenha todos os dados no Dashboard.
        """
        if not self.active_plot_frame: return
        
        # 1. Define qual arquivo é o "Principal" (Ativo) para Onda/Spec/RMS
        filename_to_plot = self.active_filename
        
        # Se não tem ativo, tenta pegar o primeiro da lista
        if not filename_to_plot and self.plot_list:
            filename_to_plot = self.plot_list[0]['filename']
        
        # Se mesmo assim não tem arquivo válido, limpa a tela e sai
        if not filename_to_plot or filename_to_plot not in self.loaded_files:
            self.active_plot_frame.clear()
            self.active_plot_frame.draw()
            return

        # Pega dados do arquivo principal
        y, sr = self.loaded_files[filename_to_plot]

        # --- ATUALIZAÇÃO DO DASHBOARD ---
        
        # A. Métricas Numéricas (Topo)
        metrics_data = self.analyzer.get_advanced_metrics(y, sr)
        if hasattr(self.active_plot_frame, 'update_metrics'):
            self.active_plot_frame.update_metrics(metrics_data)

        # B. FFT (Multi-plot: Desenha todos da lista)
        fft_frame = self.active_plot_frame.get_frame('FFT')
        fft_frame.reset_axes(self.grid_enabled)
        
        for plot_item in self.plot_list:
            fname = plot_item['filename']
            if fname not in self.loaded_files: continue
            
            y_fft, sr_fft = self.loaded_files[fname]
            
            freq, L, R = self.analyzer.get_fft_data(
                y_fft, sr_fft, self.fi, self.fm, self.fft_scale
            )
            
            # Usa 'label' (apelido) se existir, senão usa o nome do arquivo
            label_text = plot_item.get('label', fname)
            fft_frame.add_plot(freq, L, R, label_text, plot_item['color'])
        
        # C. Gráficos de Arquivo Único (Baseados em y, sr do arquivo ativo)
        
        # Forma de Onda
        times, y_data = self.analyzer.get_waveform_data(y, sr)
        self.active_plot_frame.get_frame('Waveform').plot(times, y_data, sr)
        
        # Espectrograma
        S_db = self.analyzer.get_spectrogram_data(y, sr)
        self.active_plot_frame.get_frame('Spectrogram').plot(S_db, sr)

        # RMS
        times_rms, rms_data = self.analyzer.get_rms_data(y, sr)
        self.active_plot_frame.get_frame('RMS').plot(times_rms, rms_data)
        
        # Hilbert
        samples, env_data = self.analyzer.get_hilbert_data(y)
        self.active_plot_frame.get_frame('Hilbert').plot(samples, env_data)
        
        # D. Finaliza desenhando tudo na tela
        self.active_plot_frame.draw()

    def update_plot_selection(self, selection_data, main_file):
        """
        Atualiza a lista de plots e define explicitamente o arquivo principal.
        """
        self.plot_list = []
        
        # 1. Monta a lista para o FFT (Vários arquivos)
        for i, (filename, label) in enumerate(selection_data):
            if filename in self.loaded_files:
                color = f"C{i % 10}" 
                self.plot_list.append({
                    'filename': filename,
                    'label': label,
                    'color': color
                })
        
        # 2. Define o arquivo ativo (Único) com base na escolha do usuário
        if main_file and main_file in self.loaded_files:
            self.active_filename = main_file
        elif self.plot_list:
            # Fallback: se não escolheu nada (improvável), pega o primeiro da lista
            self.active_filename = self.plot_list[0]['filename']
        else:
            self.active_filename = None
            
        self.draw_plots()

    def add_active_file_to_plot(self):
        """Botão 'Analisar' rápido (sem dialog)"""
        if self.active_filename is None: return
        
        color = f"C{len(self.plot_list)}"
        self.plot_list.append({
            'filename': self.active_filename,
            'label': self.active_filename,
            'color': color
        })
        self.draw_plots()
    
    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.draw_plots()
    
    def update_analysis_params(self, fi=None, fm=None, fft_scale=None):
        if fi is not None: self.fi = fi
        if fm is not None: self.fm = fm
        if fft_scale is not None: self.fft_scale = fft_scale
        
        # Redesenha apenas se já houver gráficos na tela
        if self.plot_list:
            self.draw_plots()
    
    def clean(self):
        """Limpa dados e tela."""
        self.loaded_files = {}
        self.active_filename = None
        self.plot_list = []
        self.draw_plots() # Isso vai limpar a tela pois plot_list está vazia
    
    def export_graph(self, dir_path: str):
        """Exporta PNGs de todos os gráficos."""
        if not self.plot_list:
            raise ValueError("Nenhum gráfico para exportar!")
        
        # 1. Dados para o FFT (Multi-linhas)
        fft_export_data = []
        for plot_item in self.plot_list:
            filename = plot_item['filename']
            if filename not in self.loaded_files: continue
            
            y_raw, sr_raw = self.loaded_files[filename]
            
            freq, L, R = self.analyzer.get_fft_data(
                y_raw, sr_raw, self.fi, self.fm, self.fft_scale
            )
            
            fft_export_data.append({
                'freq': freq, 'L': L, 'R': R,
                'label': plot_item.get('label', filename),
                'color': plot_item['color']
            })

        # 2. Dados para os outros gráficos (Arquivo Ativo)
        active_audio_data = None
        if self.active_filename and self.active_filename in self.loaded_files:
            active_audio_data = self.loaded_files[self.active_filename]

        # 3. Salva
        try:
            return self.exporter.save_dashboard(
                dir_path=dir_path,
                active_audio=active_audio_data,
                plot_list=fft_export_data,
                analyzer=self.analyzer,
                grid_enabled=self.grid_enabled,
                params={'fi': self.fi, 'fm': self.fm, 'scale': self.fft_scale}
            )
        except Exception as e:
            raise ValueError(f"Erro ao exportar: {e}")