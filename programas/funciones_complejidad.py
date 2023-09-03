""" Funciones que nos ayudarán Calcular las probabilidades de los n-gramas"""
import numpy as np


def aplicar_algoritmo(datos):
    """Calculamos el promedio de la probabilidad de los n-gramas sin autocoincidencia"""
    level = 1
    ngramas = {}
    ngramas[f'gram_{level}'] = list(map(nombre, list(set(datos))))
    ngramas[f'pos_{level}'] = {}
    ngramas[f'count_{level}'] = {}
    """ encontramos el alfabeto y las ocurrencias con lo siguiente"""
    for datos_str in ngramas[f'gram_{level}']:
        ngramas[f'pos_{level}'][datos_str] = [x for x, val in enumerate(datos)
                                                 if nombre(val) == datos_str]
        ngramas[f'count_{level}'][datos_str] = len(ngramas[f'pos_{level}'][datos_str]) - 1


    while any(list(ngramas[f'count_{level}'].values())):
        level += 1
        ngramas[f'gram_{level}'] = []
        ngramas[f'pos_{level}'] = {}
        ngramas[f'count_{level}'] = {}
        for n_gram in ngramas[f'gram_{level-1}']:
            for j in ngramas[f'pos_{level-1}'][str(n_gram)]:
                if j+level-1 < len(datos):
                    datos_str = nombre(datos[j:j+level])
                    if not datos_str in ngramas[f'pos_{level}']:
                        ngramas[f'gram_{level}'].append(datos_str)
                        ngramas[f'pos_{level}'][datos_str] = [j]
                        ngramas[f'count_{level}'][datos_str] = 0
                    else:
                        ngramas[f'pos_{level}'][datos_str].append(j)
                        ngramas[f'count_{level}'][datos_str] += 1
                else:
                    break
    del ngramas[f'gram_{level}']
    del ngramas[f'count_{level}']
    del ngramas[f'pos_{level}']
    
    proba = probabilidades(ngramas, level, len(datos))
    
    return [ngramas, proba]            
                    

def probabilidades(ngramas, level, long_datos):
    proba_ngram = []
    long_alfa_ngram = []
    for i in range(1, level):
        rep = np.array(list(ngramas[f'count_{i}'].values()), dtype=float)
        rep_plus = rep + np.ones(len(rep), dtype=float)
        proba_ngram.append(np.dot(rep/(long_datos-i), rep_plus)/(long_datos-i+1))
        long_alfa_ngram.append(len(ngramas[f'gram_{i}']))
    
    return {'Probabilidades': proba_ngram, 
             'Longitud alfabeto': long_alfa_ngram}

    
def nombre(datos_lista):
    if isinstance(datos_lista, list):
        datos_str = "["
        for i in datos_lista:
            datos_str += str(i) + ", "
        datos_str = datos_str[:-2] + "]"
        return datos_str
    else:
        return str(datos_lista) 
    