import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

class Graphic:
    def __init__(self, frame, grid_enabled=True):
        self.grid_enabled = grid_enabled

        self.fig, (self.ax_left, self.ax_right) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.subplots_adjust(wspace=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.reset_axes()  # desenha eixos iniciais com a grade

    def reset_axes(self):
        for ax in [self.ax_left, self.ax_right]:
            ax.clear()
            ax.set_facecolor('white')
            ax.set_xlabel("Frequência (Hz)", fontsize=10)
            ax.set_ylabel("Amplitude (normalizada)", fontsize=10)
            ax.grid(self.grid_enabled, which='both', linestyle=':', color='gray', alpha=0.5 if self.grid_enabled else 0.0)
        
        self.ax_left.set_title("Canal Esquerdo", fontsize=12, pad=10)
        self.ax_right.set_title("Canal Direito", fontsize=12, pad=10)
        self.canvas.draw()