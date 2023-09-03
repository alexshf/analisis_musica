from funciones_auxiliares import hacer_carpeta, json_datos, abrir_json
from funciones_complejidad import aplicar_algoritmo
import numpy as np
import os


def calcular_aleatorios(dato, lon, alfab, path):
    repeticiones = 100
    tipos = ["Equiprobable", "Bootstrap"]
    for tipo in tipos:
        path_tipo = os.path.join(path, tipo)
        if not (os.path.isfile(os.path.join(path_tipo, f"{tipo}_std.txt"))
                and os.path.isfile(os.path.join(path_tipo, f"{tipo}_media.txt"))):
            aleatorios(path_tipo, repeticiones, tipo=tipo,
                                long=lon, alfabeto=alfab, datos=dato)
            media_aleatorios_equiprobable(path_tipo, tipo, repeticiones)


def aleatorios(path, repeticiones, tipo=None, 
                        long=None, alfabeto=None, datos=None):
    path_prob = os.path.join(path, "Probabilidades")
    path_ngram = os.path.join(path, "Ngramas")
    hacer_carpeta(path)
    hacer_carpeta(path_prob)
    hacer_carpeta(path_ngram)
    
    for i in range(0, repeticiones):
        if tipo == "Equiprobable":
            aleatorio = np.random.randint(alfabeto, size=long)
        elif tipo == "Bootstrap":
            aleatorio = np.random.permutation(datos)
 
        [ngramas, probabilidades] = aplicar_algoritmo(aleatorio)
        
        ## guardamos los datos
        json_datos(path_prob, f"{tipo} {i+1}", probabilidades)
                    
        ## guardamos los ngramas
        json_datos(path_ngram, f"{tipo} {i+1}", ngramas)
        

def media_aleatorios_equiprobable(path, tipo, repeticiones):
    path_prob = os.path.join(path, "Probabilidades")
    directorio = os.listdir(path_prob)
    
    if len(directorio) < repeticiones:
        print(f'faltan aleatorios en {path_prob}')

    prob = np.zeros((20, repeticiones))
    l_al = np.zeros((20, repeticiones))
    max_len = 0
    
    for ind in range(0, repeticiones):
        proba = abrir_json(os.path.join(path_prob, f"{tipo} {ind+1}.txt"))        
        dato = proba["Probabilidades"]
        l_alfa = proba["Longitud alfabeto"]
        
        max_len = max([max_len, len(dato)])
        for h in range(0, 20):
            if h < len(dato):
                prob[h][ind] = dato[h]
                l_al[h][ind] = l_alfa[h]
            else:
                break

    prob = prob[0:max_len, :]
    l_al = l_al[0:max_len, :]
    
    prob_std = list(np.std(prob, axis=1))
    l_al_std = list(np.std(l_al, axis=1))
    
    prob = list(np.mean(prob, axis=1))
    l_al = list(np.mean(l_al, axis=1))
   
    guardar = {'Media_prob': prob, 'Std_prob': prob_std,
               'Media_alfabeto': l_al, 'Std_alfabeto': l_al_std}
    ## guardamos los datos
    json_datos(path_prob, f"{tipo}_promedios", guardar)
