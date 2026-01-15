import os
from scipy.io.wavfile import read
from model.audio_analyzer import AudioAnalyzer
from view.components.plot_frames import DashboardFrame
from view.services.plot_exporter import PlotExporter
from view.windows.loading_window import LoadingWindow

class AppController:
    def __init__(self, ui_plot_container):
        self.analyzer = AudioAnalyzer()
        self.exporter = PlotExporter()

        self.plot_container = ui_plot_container 
        self.active_plot_frame = None 

        self.loaded_files = {} 
        self.active_filename = None
        self.plot_list = [] 

        self.zoom_mode_active = False
        self.cursor_mode_active = False
        
        self.grid_enabled = True
        self.fi = 20
        self.fm = 20000
        self.fft_scale = 1

        self.active_charts = [
            "Waveform", "Spectrogram", "Pitch", "SFFT3D", 
            "Hilbert", "FFT", "RMS"
        ]

    def load_file(self, file_path):
        """
        Lê um arquivo WAV e retorna (fs, x_float).
        Converte para float entre [-1, 1] se estiver em inteiro.
        """
        try:
            fs, x = read(file_path)
            if x.dtype.kind in ('i', 'u'):
                max_val = 2 ** (8 * x.dtype.itemsize - 1)
                x = x.astype('float32') / max_val
            else:
                x = x.astype('float32')
            if len(x.shape) == 2 and x.shape[1] > 1:
                x = (x[:, 0] + x[:, 1]) / 2.0

            filename = os.path.basename(file_path)

            self.loaded_files[filename] = (x, fs)
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
        self._update_frames_visibility()
        self.draw_plots()

    def draw_plots(self):
        """Desenha APENAS o que está na lista self.active_charts."""
        if not self.active_plot_frame: return

        root = self.plot_container.winfo_toplevel()
        loading = LoadingWindow(root, message="Processando...")
        root.update()
        
        try:
            filename_to_plot = self.active_filename
            if not filename_to_plot and self.plot_list:
                filename_to_plot = self.plot_list[0]['filename']
            
            if not filename_to_plot or filename_to_plot not in self.loaded_files:
                self.active_plot_frame.clear()
                self.active_plot_frame.draw()
                return

            x, fs = self.loaded_files[filename_to_plot]

            if "FFT" in self.active_charts:
                self._update_fft_graph()
            
            # 2. Espectrograma
            if "Spectrogram" in self.active_charts:
                t_spec, f_spec, Sxx_db = self.analyzer.calcular_espectrograma(
                    x, fs, fmin=self.fi, fmax=self.fm
                )
                self.active_plot_frame.get_frame('Spectrogram').plot(t_spec, f_spec, Sxx_db)

            # 1. Waveform
            if "Waveform" in self.active_charts:
                t_wave, y_wave = self.analyzer.get_waveform_data(x, fs)
                self.active_plot_frame.get_frame('Waveform').plot(t_wave, y_wave)

            # 3. Pitch (Via Hilbert - Verde)
            if "Pitch" in self.active_charts:
                t_pitch, f0_data = self.analyzer.get_instantaneous_frequency(x, fs)
                self.active_plot_frame.get_frame('Pitch').plot(t_pitch, f0_data)

            # 4. SFFT 3D (O mais pesado de todos!)
            if "SFFT3D" in self.active_charts:
                T, F_grid, Zxx_mag = self.analyzer.get_sfft_3d_data(x, fs, fmin=self.fi, fmax=self.fm)
                self.active_plot_frame.get_frame('SFFT3D').plot(T, F_grid, Zxx_mag)

            # 5. Hilbert (Envoltória - Vermelho)
            if "Hilbert" in self.active_charts:
                t_hilbert, env_hilbert = self.analyzer.get_hilbert_envelope(x, fs)
                self.active_plot_frame.get_frame('Hilbert').plot(t_hilbert, env_hilbert)

            # 6. RMS
            if "RMS" in self.active_charts:
                t_rms, y_rms = self.analyzer.get_rms_data(x, fs)
                self.active_plot_frame.get_frame('RMS').plot(t_rms, y_rms)

            # 7. FFT e Métricas 
            metrics_data = self.analyzer.get_metrics(x, fs, fmin=self.fi, fmax=self.fm)
            if hasattr(self.active_plot_frame, 'update_metrics'):
                self.active_plot_frame.update_metrics(metrics_data)
            
            # Finaliza
            if hasattr(self.active_plot_frame, 'update_all_grids'):
                self.active_plot_frame.update_all_grids(self.grid_enabled)
            
            self.active_plot_frame.update_layout(self.active_charts)
            self.active_plot_frame.draw()
            
        except Exception as e:
            print(f"Erro ao desenhar: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            loading.destroy()

    def _update_fft_graph(self):
        # Verifica também aqui para evitar processamento desnecessário nos sliders
        if not self.active_plot_frame or "FFT" not in self.active_charts: return

        fft_frame = self.active_plot_frame.get_frame('FFT')
        fft_frame.reset_axes(self.grid_enabled)
        
        for plot_item in self.plot_list:
            fname = plot_item['filename']
            if fname not in self.loaded_files: continue
            
            x, fs = self.loaded_files[fname]
            
            f, mag = self.analyzer.calcular_fft_basica(
                x, fs, fmin=self.fi, fmax=self.fm
            )

            if self.fft_scale > 1:
                step = int(self.fft_scale)
                f = f[::step]
                mag = mag[::step]
            
            label_text = plot_item.get('label', fname)
            fft_frame.add_plot(f, mag, label_text, plot_item['color'])
        
        self.active_plot_frame.draw()
    
    def update_analysis_params(self, fi=None, fm=None, fft_scale=None):
        """Chamado pelos sliders/botão aplicar"""
        changed = False

        if fi is not None and fi != self.fi: 
            self.fi = fi
            changed = True
        if fm is not None and fm != self.fm: 
            self.fm = fm
            changed = True
        if fft_scale is not None and fft_scale != self.fft_scale: 
            self.fft_scale = fft_scale
            changed = True
        
        # SE MUDOU PARÂMETRO 
        if changed and self.plot_list:
            self.draw_plots()

    # Em AppController.py

    # Atualize a assinatura do método
    def update_plot_selection(self, selection_data, main_file, active_charts=None):
        """Atualiza quais arquivos e QUAIS GRÁFICOS serão mostrados."""
        self.plot_list = []
        
        # Atualiza lista de arquivos para FFT
        for i, (filename, label) in enumerate(selection_data):
            if filename in self.loaded_files:
                color = f"C{i % 10}" 
                self.plot_list.append({
                    'filename': filename, 'label': label, 'color': color
                })
        
        # Atualiza arquivo principal
        if main_file and main_file in self.loaded_files:
            self.active_filename = main_file
        elif self.plot_list:
            self.active_filename = self.plot_list[0]['filename']
        else:
            self.active_filename = None

        if active_charts is not None:
            self.active_charts = active_charts
            self._update_frames_visibility()
            
        self.draw_plots()
    
    def _update_frames_visibility(self):
        """Reorganiza o layout em GRID (2 colunas) para evitar buracos."""
        if not self.active_plot_frame: return
        
        # 1. Ordem de exibição desejada
        ordered_charts = [
            "FFT",
            "Spectrogram",
            "Waveform",  
            "Pitch", 
            "SFFT3D", 
            "Hilbert", 
            "HilbertFreq",  
            "RMS"
        ]
        
        # 2. Reseta o layout (Remove tudo do grid)
        # Nota: metrics_view fica sempre fixo no row=0, não removemos ele
        for frame in self.active_plot_frame.frames.values():
            frame.grid_forget()
        
        # 3. Distribui os ativos em 2 colunas
        current_row = 1 # Começa na linha 1 (a 0 é das métricas)
        current_col = 0
        
        for chart_name in ordered_charts:
            if chart_name in self.active_charts:
                frame = self.active_plot_frame.get_frame(chart_name)
                if frame:
                    # Casos especiais: Gráficos muito largos ou importantes podem ocupar 2 colunas
                    # Por exemplo, se quiser que o FFT ou 3D ocupe a linha toda:
                    if chart_name in ["FFT", "SFFT3D"] and False: # Mude False para True se quiser destaque
                        # Se já estamos na coluna 1, avança para a próxima linha para começar limpo
                        if current_col == 1:
                            current_row += 1
                            current_col = 0
                        
                        frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5, padx=5)
                        current_row += 1
                        current_col = 0 # Próximo começa na esquerda
                    else:
                        # Padrão: Ocupa 1 coluna
                        frame.grid(row=current_row, column=current_col, sticky="ew", pady=5, padx=5)
                        
                        # Avança a posição
                        current_col += 1
                        if current_col > 1: # Se passou da coluna 1 (foi pra 2), reseta
                            current_col = 0
                            current_row += 1

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
        
        # Se temos um gráfico ativo na tela
        if self.active_plot_frame:
            # Se for o Dashboard, manda atualizar todos dentro dele
            if hasattr(self.active_plot_frame, 'update_all_grids'):
                self.active_plot_frame.update_all_grids(self.grid_enabled)
            
            # Se for um gráfico sozinho (caso use no futuro), atualiza ele
            elif hasattr(self.active_plot_frame, 'set_grid'):
                self.active_plot_frame.set_grid(self.grid_enabled)
    
    def clean(self):
        """Limpa dados e tela."""
        self.loaded_files = {}
        self.active_filename = None
        self.plot_list = []
        self.draw_plots() # Isso vai limpar a tela pois plot_list está vazia

    def toggle_zoom_mode(self):
        """Alterna entre modo Zoom e Normal."""
        if not self.active_plot_frame: return False
        
        self.zoom_mode_active = not self.zoom_mode_active
        
        if self.zoom_mode_active and self.cursor_mode_active:
            self.cursor_mode_active = False
            self.active_plot_frame.set_cursor_mode(False)

        # Chama o Dashboard para aplicar em todos
        self.active_plot_frame.set_zoom_mode(self.zoom_mode_active)
        
        return self.zoom_mode_active # Retorna estado para mudar cor do botão na View

    def toggle_cursor_mode(self):
        """Lógica inteligente: Se ligar Cursor, desliga Zoom."""
        if not self.active_plot_frame: return False
        
        self.cursor_mode_active = not self.cursor_mode_active
        
        # Aplica Cursor
        self.active_plot_frame.set_cursor_mode(self.cursor_mode_active)
        
        # SE ligou Cursor, DESLIGA Zoom
        if self.cursor_mode_active and self.zoom_mode_active:
            self.zoom_mode_active = False
            self.active_plot_frame.set_zoom_mode(False)
            
        return self.cursor_mode_active

    def reset_zoom(self):
        """Reseta todos os gráficos."""
        if self.active_plot_frame:
            self.active_plot_frame.reset_all_zooms()
            # Opcional: Desativar o modo zoom ao resetar
            # self.zoom_mode_active = False
            # self.active_plot_frame.set_zoom_mode(False)
    
    def export_graph(self, dir_path: str):
        if not self.plot_list:
            raise ValueError("Nenhum gráfico para exportar!")
        
        # 1. Prepara dados do FFT (mantido igual)
        fft_export_data = []
        # Só processa FFT se ele estiver ativo no dashboard
        if "FFT" in self.active_charts:
            for plot_item in self.plot_list:
                filename = plot_item['filename']
                if filename not in self.loaded_files: continue
                
                x_raw, fs_raw = self.loaded_files[filename]
                f, mag = self.analyzer.calcular_fft_basica(
                    x_raw, fs_raw, fmin=self.fi, fmax=self.fm
                )
                
                if self.fft_scale > 1:
                    step = int(self.fft_scale)
                    f = f[::step]
                    mag = mag[::step]
                
                fft_export_data.append({
                    'freq': f, 'mag': mag, 
                    'label': plot_item.get('label', filename),
                    'color': plot_item['color']
                })

        # 2. Dados do Áudio Ativo
        active_audio_data = None
        if self.active_filename and self.active_filename in self.loaded_files:
            active_audio_data = self.loaded_files[self.active_filename]

        # 3. Salva passando a lista self.active_charts
        try:
            return self.exporter.save_dashboard(
                dir_path=dir_path,
                active_audio=active_audio_data,
                plot_list=fft_export_data,
                analyzer=self.analyzer,
                grid_enabled=self.grid_enabled,
                params={'fi': self.fi, 'fm': self.fm},
                active_charts=self.active_charts  # <--- NOVA LINHA IMPORTANTE
            )
        except Exception as e:
            print(f"Erro na exportação: {e}")
            raise e