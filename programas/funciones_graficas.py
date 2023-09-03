import matplotlib.pyplot as plt
import numpy as np
import itertools
import math


def graf_ngrama(eje_x, eje_y, df, generos, claves, n_grams, log=False):
    if log:
        lo = 'log '
    else:
        lo = ''
    wi, he = plt.figaspect(2.)
    he = 9 * he / 10
    fuente_img = 12
    fuente_legend = 4.5
    tam = math.ceil(math.sqrt(len(n_grams)))
    fig, axs = plt.subplots(tam, tam)
    ind_x = 0
    ind_y = 0
    for n in n_grams:
        ind_et2 = 0
        for gen in generos:
            ind_et = 0
            datos = df[df["etiquetas_genero"] == gen]
            for cla in list(reversed(claves)):
                ##### Código para poner etiquetas (se repiten los aleatorios por género
                ##### así que los quitamos
                if ind_et2 == 0 and ind_et != len(claves)-1:
                    etiqueta = cla
                elif ind_et == len(claves)-1:
                    etiqueta = gen[0:3]
                else:
                    etiqueta = '_nolegend_'

                ## este código es pa grafica
                axs[ind_x, ind_y].scatter(datos[eje_x],
                                          datos[f'{lo}{eje_y}_{cla}: N_gram {n}'],
                                          c=datos[f"color {cla}"],
                                          marker=datos[f"marcador {cla}"][0],
                                          label=etiqueta)
                ## para generar titulos de subplots
                axs[ind_x, ind_y].set_title(f"{n}-gram")
                ind_et += 1 #algo de etiquetas
            ind_et2 += 1 # algo de etiquetas
        #más código de etiquetas
        if ind_x == 0 and ind_y == tam:
            axs[ind_x, ind_y].legend(bbox_to_anchor=(1, 1))
        ind_y = (ind_y + 1) % tam
        if ind_y == 0:
            ind_x += 1
        fig.show()
        print('fig', fig)
        print('ejes', axs)

def graf_ngrama_genero(eje_y, df, generos, claves, n_grams):
    wi, he = plt.figaspect(2.)
    he = 9 * he / 10
    fuente_img = 12
    fuente_legend = 4.5
    fig, axs = plt.subplots()
    ind_x = 0
    ind_y = 0
    ind_et2 = 0
    for gen in generos:
        ind_et = 0
        datos = df[df["etiquetas_genero"] == gen]
        datos_x = np.arange(n_grams[0], n_grams[1], 1)
        for cla in list(reversed(claves)):
            if ind_et2 == 0 and ind_et != 2:
                etiqueta = cla
            elif ind_et == 2:
                etiqueta = gen
            else:
                etiqueta = '_nolegend_'
            ind_et += 1
            datos_y = []
            for n in range(n_grams[0], n_grams[1]):
                datos_y.append(datos[f'{eje_y}_{cla}: N_gram {n}'].mean(axis=0))
                ## este código es pa graficar
            axs.scatter(datos_x, datos_y,
                        c=list(itertools.repeat(datos[f"color {cla}"][0], len(datos_x))),
                        marker=datos[f"marcador {cla}"][0],
                        label=etiqueta)
        ## para generar titulos de subplots
        ind_et2 += 1
    axs.set_title(f"N-gram mea")
    axs.legend(bbox_to_anchor=(1, 1))
