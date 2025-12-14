from numpy import sqrt, mean, std, square, abs, correlate, argmax, array
from scipy.signal import hilbert
from scipy.io import wavfile
from matplotlib.pyplot import plot, xlabel, ylabel, title, legend, show

dados = [0.2, -0.4, 0.6, -0.8, 1.0, -1.0, 0.5, -0.3]

#Para Calcular o RMS use a seguinte sequência de funções
#------------------------------------------------------------------------------
#dados deve ser uma lista, vindo ou do ESP ou algum dado interno do programa.
rms = sqrt(mean(square(dados)))
#------------------------------------------------------------------------------

#Para calcular o máximo e o mínimo de um lista
#------------------------------------------------------------------------------
#dados deve ser uma lista.
maximo = max(dados)
minimo = min(dados)
#------------------------------------------------------------------------------


#Neste caso, é para colocar estes valores ao lado dos gráficos de Hilbert, etc
#------------------------------------------------------------------------------

#Ler um arquivo de áudio (estabelecer se estéreo ou mono. Se mono, um 
#canal apenas. Se estéreo, aplicar para ambos canais.)
fs, sinal = wavfile.read("file_example_WAV_1MG.wav")
sinal = sinal.astype(float)

if sinal.ndim == 2:
    sinal = sinal[:, 0]  # canal esquerdo

#Transformada de Hilbert
sinal_analitico = hilbert(sinal)
envelope = abs(sinal_analitico)

#RMS
rms = sqrt(mean(square(sinal)))

#Estimativa de pitch (simplificada via autocorrelação)

perfil = "robusto"

# Perfil robusto (o usuário deve escolher entre Robusto ou Equilibrado
if perfil == "robusto":
    janela = int(0.2 * fs)
    passo  = int(0.05 * fs)
else:
 # Perfil equilibrado
    janela = int(0.1 * fs)
    passo  = int(0.025 * fs)


pitches = []

for i in range(0, len(sinal) - janela, passo):
    trecho = sinal[i:i+janela]
    trecho = trecho - mean(trecho)  # remover DC
    corr = correlate(trecho, trecho, mode="full")
    corr = corr[len(corr)//2:]  # metade positiva
    pico = argmax(corr[1:]) + 1
    if pico > 0:
        freq = fs / pico
        pitches.append(freq)

pitches = array(pitches)

#Estatística do pitch
media_pitch = mean(pitches)
desvio_pitch = std(pitches)
resultado = f"{media_pitch:.2f} ± {desvio_pitch:.2f} Hz"


#Gráfico da variação do pitch (acrescentar este gráfico, por favor, se não tiver.
plot(pitches, label="Pitch estimado (Hz)")
xlabel("Janela de análise")
ylabel("Frequência (Hz)")
title("Variação do Pitch")
legend()
show()
#------------------------------------------------------------------------------