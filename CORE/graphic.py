import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class Graphic:
    def __init__(self, frame, grid_enabled=True):
        self.grid_enabled = grid_enabled

        # Tema escuro
        plt.style.use("dark_background")

        # Figura com fundo transparente (para casar com o CTkFrame)
        self.fig, (self.ax_left, self.ax_right) = plt.subplots(1, 2, figsize=(12, 5), facecolor="#2b2b2b")
        self.fig.subplots_adjust(wspace=0.3)

        # Canvas embedado no Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.reset_axes()  # desenha eixos iniciais

    def reset_axes(self):
        for ax in [self.ax_left, self.ax_right]:
            ax.clear()

            # Cores de fundo e eixos
            ax.set_facecolor("#1e1e1e")
            ax.tick_params(colors="white", labelsize=9)
            ax.spines["bottom"].set_color("white")
            ax.spines["left"].set_color("white")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            # Labels
            ax.set_xlabel("Frequência (Hz)", fontsize=10, color="white", labelpad=8)
            ax.set_ylabel("Amplitude (normalizada)", fontsize=10, color="white", labelpad=8)

            # Grid
            ax.grid(
                self.grid_enabled,
                which="both",
                linestyle=":",
                linewidth=0.7,
                color="gray",
                alpha=0.4 if self.grid_enabled else 0.0,
            )

        # Títulos dos gráficos
        self.ax_left.set_title("Canal Esquerdo", fontsize=12, color="cyan", pad=12)
        self.ax_right.set_title("Canal Direito", fontsize=12, color="cyan", pad=12)

        self.canvas.draw()
