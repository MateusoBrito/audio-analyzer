import librosa
import os

class AudioController:
    """
    Controla o carregamento, armazenamento e acesso aos dados de áudio.
    
    Esta classe é a única fonte de verdade sobre o arquivo de áudio
    atualmente em análise na aplicação.
    """
    def __init__(self):
        self.y = None  # A série temporal do áudio (amostras)
        self.sr = None # A taxa de amostragem (sample rate)
        self.file_path = None

    def load_file(self, file_path):
        """
        Carrega um arquivo de áudio usando Librosa e armazena os dados.
        
        Args:
            file_path (str): O caminho para o arquivo de áudio.
            
        Returns:
            bool: True se o carregamento foi bem-sucedido, False caso contrário.
        """
        try:
            self.y, self.sr = librosa.load(file_path, sr=None)
            self.file_path = file_path
            print(f"Áudio carregado: {self.get_filename()}")
            return True
        except Exception as e:
            print(f"Erro ao carregar o arquivo de áudio: {e}")
            self.clear_audio() # Garante que o estado fique limpo em caso de erro
            return False

    def get_audio_data(self):
        """
        Retorna os dados do áudio atualmente carregado.
        
        Returns:
            tuple: Uma tupla (y, sr) com os dados e a taxa de amostragem.
                   Retorna (None, None) se nada estiver carregado.
        """
        return self.y, self.sr

    def is_loaded(self):
        """
        Verifica se há um arquivo de áudio carregado.
        
        Returns:
            bool: True se um áudio está carregado, False caso contrário.
        """
        return self.y is not None and self.sr is not None

    def get_filename(self):
        """

        Retorna apenas o nome do arquivo, sem o caminho completo.
        
        Returns:
            str: O nome do arquivo ou uma string vazia.
        """
        return os.path.basename(self.file_path) if self.file_path else ""

    def clear_audio(self):
        """
        Limpa os dados do áudio da memória, resetando o estado.
        """
        self.y = None
        self.sr = None
        self.file_path = None
        print("Dados de áudio limpos.")