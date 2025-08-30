import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class Graphic:
    def __init__(self, frame):
        self.fig, (self.ax_left, self.ax_right) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.subplots_adjust(wspace=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

"""
if __name__ == "__main__":
    plt.switch_backend("Agg")
    plt.style.use("default")

    app = ctk.CTk()
    app.title("Sounder Analyzer")
    app.geometry("900x500")
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure((0, 1), weight=1)
    app.config(bg="#f0f0f0")

    graph_container = ctk.CTkFrame(app, fg_color="white", corner_radius=0)
    graph_container.pack(fill=ctk.BOTH, expand=True)

    # Área de gráficos
    graphic = Graphic(graph_container)

    app.mainloop()
"""
