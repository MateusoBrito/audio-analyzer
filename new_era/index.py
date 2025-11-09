import tkinter as tk
from tkinter import filedialog, messagebox
import new_era.arquivo as fp
import new_era.audio as pa

class OpenFile:
    def __init__(self):
        self.file_path = None
        self.file = fp.File()

        self.raw_data, self.sample_rate, self.file_name = self.upload_window()


    def upload_window(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos WAV", "*.wav")])
        if not file_path:
            return
        
        try:
            self.file.load_file(file_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar áudio: {str(e)}")

        return self.load_file.get_file()


def main():
    """
    Função principal do programa.
    Cria a janela raiz do Tkinter e inicia o processo de abertura de arquivo.
    """
    root = tk.Tk()
    root.withdraw()  # esconde a janela principal, deixando apenas o diálogo de seleção
    OpenFile()       # cria e executa o processo de seleção e carregamento
    root.mainloop()  # mantém o loop do Tkinter ativo (necessário para messagebox etc.)


if __name__ == "__main__":
    main()