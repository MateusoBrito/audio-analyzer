from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GraphicsController:
    """
    Controla a exibição de uma única figura Matplotlib dentro de um frame pai.
    
    Esta classe gerencia o ciclo de vida de um canvas de gráfico:
    criação, atualização (substituindo o antigo) e exclusão.
    """
    def __init__(self, parent_frame):
        """
        Inicializa o controlador.
        
        Args:
            parent_frame (ctk.CTkFrame): O frame onde o gráfico será desenhado.
        """
        self.parent_frame = parent_frame
        self.canvas_widget = None

    def create_graph(self, fig):
        """
        Recebe uma figura Matplotlib, apaga qualquer gráfico antigo e desenha o novo.
        """
        # Se já existe um gráfico, apaga antes de criar o novo
        if self.canvas_widget:
            self.delete_graph()

        # Fecha a figura para liberar memória depois que o canvas a assumir
        plt.close(fig)

        # Cria o canvas do Tkinter que vai conter a figura
        canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        canvas.draw()
        
        # Pega o widget do Tkinter e o posiciona no frame pai
        widget = canvas.get_tk_widget()
        widget.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Guarda uma referência ao widget para poder apagá-lo depois
        self.canvas_widget = widget

    def update_graph(self, fig):
        """
        Apelido para create_graph. A lógica de atualização mais limpa
        é sempre destruir o antigo e criar um novo.
        """
        self.create_graph(fig)

    def delete_graph(self):
        """
        Remove o gráfico atual do frame.
        """
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None