import numpy as np
from scipy.signal import hilbert
import matplotlib.pyplot as plt

# Criando um sinal senoidal
t = np.linspace(0, 1, 1000)
sinal = np.sin(2 * np.pi * 5 * t)

# Aplicando a transformada de Hilbert
sinal_analitico = hilbert(sinal)

# Extraindo o envelope
envelope = np.abs(sinal_analitico)

# Visualizando
plt.figure()
plt.plot(t, sinal, label='Sinal original')
plt.plot(t, envelope, label='Envelope', linestyle='--')
plt.legend()
plt.title('Transformada de Hilbert')
