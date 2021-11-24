########## SIMULACIÓN DE EVENTOS DISCRETOS ##########
## al finalizar le programa, eliminar los print() que solo sirvieron para depuración ##
from pprint import pprint
import random
import math
import numpy as np
## DECLARACIÓN DE VALORES ###
DIFS = 10e-3
SIFS = 5e-3
durRTS = 11e-3
durCTS = 11e-3
durACK = 11e-3
durDATA = 43e-3
sigma = 1e-3 #tamaño de miniranuras
H = 7 #grados
paquetes_descartados = [0 for h in range(H)] #paquetes descartados por grado
paquetes_generados = [0 for h in range(H)] #paquetes generados por grado
K = 15 #tamaño del buffer
sleep = 18 #número de ranuras dormir
#nodos_por_grado = [5,10,15,20]
nodos_por_grado = [5]
#windows_size = [16,32,64,128,256]
windows_size = [16]
#lambda1 = [0.0005,0.001,0.005,0.03]
lambda1 = [0.0005]
# Ciclos 300000
ciclos = 5000
# Paquetes que llegan al nodo sink
paquetes_nodo_sink = [0]

#PROCESO DE GENERACIÓN DE PAQUETES
def proceso_gen_paquetes(N,W,lambdda,nodos):
    lambda2 = lambdda * N * H
    U = ((1e6)*random.uniform(0,0.01))/1e6
    nuevot = -(1/lambda2)*math.log(1-U)
    # print(nuevot)
    nodo = random.randint(1,N)
    grado = random.randint(1,H)
    # print("Nodo: {nodo}".format(nodo=nodo))
    # print("Grado: {grado}".format(grado=grado))
    if nodos[grado-1][nodo-1] < K:
        nodos[grado-1][nodo-1] += 1
    else:
        paquetes_descartados[grado-1] += 1
    paquetes_generados[grado-1] += 1
    #NUEVO ARRIBO
    return nuevot

def proceso_transmision(nodos, W, N, ciclo):
    # Grados del mayor al menor
    for grado in range(H,0,-1):
        nodos_contadores = [0 for i in range(N)]
        for nodo in range(N):
            # Asignar un contador a aquellos nodos con paquetes
            if nodos[grado-1][nodo-1] != 0:
                nodos_contadores[nodo-1] = random.randint(0,W-1)
            else:
                # Le asigno W porque no puedo usar min() con None
                nodos_contadores[nodo-1] = W
            
        # Determinar el nodo ganador o si es que no hay, poner -1
        minimo = min(nodos_contadores);
        menor_ranura = minimo if minimo < W else -1
        
        # print(f'\n Contadores nodos grado {grado}')
        # pprint(nodos_contadores)
        
        # print(f'Menor ranura: {menor_ranura}')
        
        # Si hay paquetes por transmitir
        if menor_ranura > -1:
            # Checar colisión (contadores repetidos)
            nodos_ganadores = [i for i, x in enumerate(nodos_contadores) if x == menor_ranura]
            
            # Remover paquetes en caso de colisión
            if len(nodos_ganadores) > 1:
                for n in nodos_ganadores:
                    nodos[grado-1][n] -= 1
                # Aumentar paquetes descartados
                paquetes_descartados[grado-1] += len(nodos_ganadores)
            else:
                # Restar al buffer del nodo
                nodos[grado-1][nodos_ganadores[0]] -= 1
                
                # Enviar paquete a nodo inferior
                if grado > 1:
                    if nodos[grado-2][nodos_ganadores[0]] < K:
                        # Si hay espacio en el buffer recibir el paquete
                        nodos[grado-2][nodos_ganadores[0]] += 1
                    else:
                        # Si no hay espacio en el buffer descartar el paquete
                        paquetes_descartados[grado-2] += 1
                else:
                    # Llegada a nodo sink
                    paquetes_nodo_sink[0] += 1
                        

#INICIALIZACIÓN DE VARIABLES CORRESPONDIENTES AL CASO
def inicializacion(N,W,lambdda):
    T = sigma*W + DIFS + 3*SIFS + durRTS + durCTS + durACK + durDATA
    ranuras_totales = (2+sleep);
    Tc = ranuras_totales*T
    nodos = [[0 for i in range(N)] for j in range(H)]
    # pprint(nodos)
    ta = -1
    tsim = 0
    i = 0
    # Basado en tiempo
    for t1 in np.arange(.1, ciclos*round(Tc,1)+.1, .1):
        if ta < tsim:
            ta = tsim + proceso_gen_paquetes(N,W,lambdda,nodos)
            # pprint(nodos)
        # incremento de tiempo de simulación
        tsim = tsim + T
        
        # Comprobar que se encuentre en Tx
        if round(t1 % round(Tc,1), 1) == .1:
            # Ciclos
            i += 1
            proceso_transmision(nodos, W, N, i)
            

for caso_nodos in nodos_por_grado:
    for caso_W in windows_size:
        for caso_lambda in lambda1:
            print("Cantidad de nodos: {nodos} \nMáximo número de miniranuras: {W} \nTasa (lambda): {lambdaa}".format(nodos=caso_nodos,W=caso_W,lambdaa=caso_lambda))
            #calculo duración de ranura, esta secuencia se deberá corregir en el diagrama
            inicializacion(caso_nodos,caso_W,caso_lambda)