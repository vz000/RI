########## SIMULACIÓN DE EVENTOS DISCRETOS ##########
## al finalizar le programa, eliminar los print() que solo sirvieron para depuración ##
from pprint import pprint
import random
import math
## DECLARACIÓN DE VALORES ###
DIFS = 10e-3
SIFS = 5e-3
durRTS = 11e-3
durCTS = 11e-3
durACK = 11e-3
durDATA = 43e-3
sigma = 1e-3 #tamaño de miniranuras
H = 7 #grados
paquetes_descartados = [0 for h in range(1,H)] #paquetes descartados por grado
K = 15 #tamaño del buffer
sleep = 18 #número de ranuras dormir
#nodos_por_grado = [5,10,15,20]
nodos_por_grado = [5]
#windows_size = [16,32,64,128,256]
windows_size = [16]
#lambda1 = [0.0005,0.001,0.005,0.03]
lambda1 = [0.0005]

#PROCESO DE GENERACIÓN DE PAQUETES
def proceso_gen_paquetes(N,W,lambdda,nodos):
    lambda2 = lambdda * N * H
    U = ((1e6)*random.uniform(0,0.01))/1e6
    nuevot = -(1/lambda2)*math.log(1-U)
    print(nuevot)
    nodo = random.randint(1,N)
    grado = random.randint(1,H)
    print("Nodo: {nodo}".format(nodo=nodo))
    print("Grado: {grado}".format(grado=grado))
    if nodos[grado-1][nodo-1] < 15:
        nodos[grado-1][nodo-1] += 1
    else:
        paquetes_descartados[grado-1] += 1
    #NUEVO ARRIBO
    return nuevot


#INICIALIZACIÓN DE VARIABLES CORRESPONDIENTES AL CASO
def inicializacion(N,W,lambdda):
    T = sigma*W + DIFS + 3*SIFS + durRTS + durACK + durDATA
    Tc = (2+sleep)*T
    nodos = [[0 for i in range(N)] for j in range(H)]
    pprint(nodos)
    ta = -1
    tsim = 0
    for t1 in range(0,int(5000*Tc)): # n*Tc para obtener la cantidad de ciclos por procesar.
        if ta < tsim:
            ta = tsim + proceso_gen_paquetes(N,W,lambdda,nodos)
            pprint(nodos)
        # incremento de tiempo de simulación
        tsim = tsim + T


for caso_nodos in nodos_por_grado:
    for caso_W in windows_size:
        for caso_lambda in lambda1:
            print("Cantidad de nodos: {nodos} \nMáximo número de miniranuras: {W} \nTasa (lambda): {lambdaa}".format(nodos=caso_nodos,W=caso_W,lambdaa=caso_lambda))
            #calculo duración de ranura, esta secuencia se deberá corregir en el diagrama
            inicializacion(caso_nodos,caso_W,caso_lambda)