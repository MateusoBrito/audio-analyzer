import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RectangleSelector

# Dados de exemplo
fig, ax = plt.subplots()
x = range(100)
y = [v**0.5 for v in x]
ax.plot(x, y)
plt.subplots_adjust(bottom=0.25)

# Guardar limites originais
xlim_original = ax.get_xlim()
ylim_original = ax.get_ylim()

# Controle de estado
zoom_ativo = [False]

# Função chamada ao selecionar região
def aplicar_zoom(eclick, erelease):
    if zoom_ativo[0]:
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        ax.set_xlim(min(x1, x2), max(x1, x2))
        ax.set_ylim(min(y1, y2), max(y1, y2))
        plt.draw()
        # Desativa zoom e remove área rosa
        zoom_ativo[0] = False
        selector.set_active(False)
        botao_zoom.label.set_text("Ativar Zoom")
        # Remove o retângulo desenhado
        selector.clear()

# Criar RectangleSelector (inicialmente desativado)
selector = RectangleSelector(ax, aplicar_zoom,
                             useblit=True,
                             button=[1],  # botão esquerdo
                             interactive=True)
selector.set_active(False)

# Função do botão de zoom
def ativar_zoom(evento):
    zoom_ativo[0] = True
    selector.set_active(True)
    botao_zoom.label.set_text("Zoom Ativado")
    plt.draw()

# Função do botão reset
def resetar_zoom(evento):
    ax.set_xlim(xlim_original)
    ax.set_ylim(ylim_original)
    plt.draw()
    # Garante que o zoom esteja desativado
    zoom_ativo[0] = False
    selector.set_active(False)
    botao_zoom.label.set_text("Ativar Zoom")
    # Remove qualquer retângulo ainda visível
    selector.clear()

# Criar botões
ax_botao_zoom = plt.axes([0.65, 0.05, 0.25, 0.075])
botao_zoom = Button(ax_botao_zoom, "Ativar Zoom")
botao_zoom.on_clicked(ativar_zoom)

ax_botao_reset = plt.axes([0.35, 0.05, 0.25, 0.075])
botao_reset = Button(ax_botao_reset, "Resetar Zoom")
botao_reset.on_clicked(resetar_zoom)

plt.show()