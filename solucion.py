########## SIMULACIÓN DE EVENTOS DISCRETOS ##########
## al finalizar le programa, eliminar los print() que solo sirvieron para depuración ##
import random
import math
import numpy as np
import matplotlib.pyplot as plt

## DECLARACIÓN DE VALORES ###
DIFS = 10e-3
SIFS = 5e-3
durRTS = 11e-3
durCTS = 11e-3
durACK = 11e-3
durDATA = 43e-3
sigma = 1e-3 #tamaño de miniranuras
H = 7 #grados
paquetes_descartados_buffer = [0 for h in range(H)] #paquetes descartados por grado
paquetes_descartados_colision = [0 for h in range(H)] #paquetes descartados por grado
paquetes_generados = [0 for h in range(H)] #paquetes generados por grado
paquetes_nodo_sink = 0 # Paquetes que llegan al nodo sink
retardos = [0 for h in range(H)]
retardos2 = [0 for h in range(H)]
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

#PROCESO DE GENERACIÓN DE PAQUETES
def proceso_gen_paquetes(N,W,lambdda,nodos):
    lambda2 = lambdda * N * H
    U = ((1e6)*random.uniform(0,0.01))/1e6
    nuevot = -(1/lambda2)*math.log(1-U)
    nodo = random.randint(1,N)
    grado = random.randint(1,H)
    if nodos[grado-1][nodo-1] < K:
        nodos[grado-1][nodo-1] += 1
    else:
        paquetes_descartados_buffer[grado-1] += 1
    paquetes_generados[grado-1] += 1
    #NUEVO ARRIBO
    return nuevot

def proceso_transmision(nodos, W, N):
    global paquetes_nodo_sink
    retardos2_helper = [0 for h in range(H)]
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
        
        # Si hay paquetes por transmitir
        if menor_ranura > -1:
            # Checar colisión (contadores repetidos)
            nodos_ganadores = [i for i, x in enumerate(nodos_contadores) if x == menor_ranura]
            
            # Remover paquetes en caso de colisión
            if len(nodos_ganadores) > 1:
                for n in nodos_ganadores:
                    nodos[grado-1][n] -= 1
                # Aumentar paquetes descartados
                paquetes_descartados_colision[grado-1] += len(nodos_ganadores)
            else:
                # Restar al buffer del nodo
                nodos[grado-1][nodos_ganadores[0]] -= 1
                
                # Enviar paquete a nodo inferior
                if grado > 1:
                    if nodos[grado-2][nodos_ganadores[0]] < K:
                        # Si hay espacio en el buffer recibir el paquete
                        nodos[grado-2][nodos_ganadores[0]] += 1
                        
                        # Retardos v2
                        retardos2_helper[grado-1] = 1
                        
                        # Paquetes que llegan al nodo
                        retardos[grado-1] += 1
                    else:
                        # Si no hay espacio en el buffer descartar el paquete
                        paquetes_descartados_buffer[grado-2] += 1
                else:
                    # Llegada a nodo sink
                    paquetes_nodo_sink += 1
                    
                    # Paquetes que llegan al nodo
                    retardos[grado-1] += 1
                    
                    # Retardos v2
                    retardos2_helper[grado-1] = 1
    
    # Función para contar retardos
    contador_retardos(retardos2_helper)

# Contar los retadors
def contador_retardos(rets):
    nodo_transmisor = H
    for i,r in reversed(list(enumerate(rets))):
        if r == 0:
            nodo_transmisor = i
    
    for i in range(nodo_transmisor):
        retardos2[i] += 1
    

#INICIALIZACIÓN DE VARIABLES CORRESPONDIENTES AL CASO
def inicializacion(N,W,lambdda):
    T = sigma*W + DIFS + 3*SIFS + durRTS + durCTS + durACK + durDATA
    ranuras_totales = (2+sleep);
    Tc = ranuras_totales*T
    nodos = [[0 for i in range(N)] for j in range(H)]
    
    ta = -1
    tsim = 0
    # Basado en tiempo
    for t1 in np.arange(.1, ciclos*round(Tc,1)+.1, .1):
        if ta < tsim:
            ta = tsim + proceso_gen_paquetes(N,W,lambdda,nodos)
        
        # Comprobar que se encuentre en Tx
        if round(t1 % round(Tc,1), 1) == .1:
            proceso_transmision(nodos, W, N)
            
        # incremento de tiempo de simulación
        tsim = tsim + T
    
    # Gráfica de paquetes perdidos
    x_axis = [x for x in range(H)]
    fig, ax = plt.subplots()
    
    p1 = ax.bar(x_axis, paquetes_descartados_colision, .9, label='Por Colisión')
    p2 = ax.bar(x_axis, paquetes_descartados_buffer, .9,
            bottom=paquetes_descartados_colision, label='Por Buffer')

    ax.axhline(0, color='grey', linewidth=0.8)
    ax.set_ylabel('Paquetes')
    ax.set_xlabel('Grados')
    ax.set_title('Paquetes Perdidos')
    ax.set_xticks([x for x in range(H)])
    ax.set_xticklabels([f'G{x}' for x in range(1,H+1)])
    ax.legend()
    
    ax.bar_label(p1, label_type='center')
    ax.bar_label(p2, label_type='center')
    ax.bar_label(p2)
    
    # Gráfica de retardos v1
    plt.figure()
    r = [ciclos/x for x in retardos]
    plt.plot(x_axis, list(reversed(r)), marker='o')
    for a,b in zip(x_axis, reversed(r)): 
        plt.text(a, b, str(round(b,2)))
    plt.title('Retardos entre grados', fontsize=14)
    plt.xlabel('Grados', fontsize=14)
    plt.ylabel('Ciclos por paquete', fontsize=14)
    plt.xticks(x_axis, list(reversed([f'G{x} - G{x-1}' for x in range(1,H+1)])))
    
    # Gráfica de retardos v2
    fig, ax = plt.subplots()
    r = [ciclos/x for x in retardos2]
    p1 = ax.bar(x_axis, r, 0.9)
    ax.set_ylabel('Ciclos por paquete')
    ax.set_xticks([x for x in range(H)])
    ax.set_xticklabels([f'G{x}' for x in range(1,H+1)])
    ax.set_title('Retardos hasta nodo sink')
    ax.bar_label(p1, label_type='center')
    plt.xticks(x_axis,[f'G{x}' for x in range(1,H+1)])
    
    # Troughput
    print(f'\nTroughput: {paquetes_nodo_sink}/{ciclos} [paquetes/ciclos]')
    
for caso_nodos in nodos_por_grado:
    for caso_W in windows_size:
        for caso_lambda in lambda1:
            print("Cantidad de nodos: {nodos} \nMáximo número de miniranuras: {W} \nTasa (lambda): {lambdaa}\n".format(nodos=caso_nodos,W=caso_W,lambdaa=caso_lambda))
            #calculo duración de ranura, esta secuencia se deberá corregir en el diagrama
            inicializacion(caso_nodos,caso_W,caso_lambda)
            
