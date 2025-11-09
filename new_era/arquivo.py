import os
import soundfile as sf

class File:
    """
    Classe responsável por carregar e armazenar informações de um arquivo de áudio.
    """

    def __init__(self):
        self.raw_data = None
        self.sample_rate = None
        self.file_name = None

    def loadFile(self, file_path):
        """
        Carrega um arquivo de áudio e armazena seus dados e informações básicas.

        Parâmetros:
            file_path (str): Caminho completo do arquivo de áudio a ser carregado.
        """
        self.raw_data, self.sample_rate = sf.read(file_path, dtype="float32")
        self.file_name = os.path.basename(file_path)

    def getFile(self):
        """
        Retorna as informações do arquivo de áudio atualmente carregado.

        Retorna:
            tuple: (raw_data, sample_rate, file_name)
        """
        return self.raw_data, self.sample_rate, self.file_name
