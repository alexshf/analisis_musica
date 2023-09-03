from funciones_auxiliares import abrir_datos, elegir_generos, \
    hacer_carpeta, generar_colores_marcadores, agregar_columna_bd, \
    json_datos, abrir_json
from funciones_graficas import graf_ngrama, graf_ngrama_genero
from procesar import hacer_titulos
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def string_tuple(celda):
    try:
        celda = eval(celda)
        return celda
    except:
        celda = celda
        return celda


def cargar_datos(rola, df, file_txt, pressition, n_gram_max, clave):
    """Rellena el excel con los n-gramas que vamos a usar de la canción enviada
    requiere el nombe, el excel df, el nombre del archivo, la presicion,
    el n-grama maximo que aceptamos y un nombre clave"""
    datos = abrir_json(file_txt)
    if "Probabilidades" in datos:
        dato = datos["Probabilidades"]
    elif 'Media_prob' in datos:
        dato = datos["Media_prob"]
        
    for n in range(0, n_gram_max):
        if n < len(dato) \
                and float(pressition.format(dato[n])) != 0:
            df.loc[rola, f'{clave}: N_gram {n+1}'] = float(pressition.format(dato[n]))
            df.loc[rola, f'log {clave}: N_gram {n+1}'] = -np.log(float(pressition.format(dato[n])))
    return df


def cargar_ngramas_random(df, variables, n_gram_max, mypath_prob,
                          mypath_rand, pressition, claves):
    """Por cada canción cargaremos las probabilidades y los aleatorios de las variables señaladas
    por ejemplo: ritmo, melodía y armonía. Cada probabilidad se guardará en df"""

    ### Agregamos columnas por cada tipo de variable, por cada tipo de dato (probabilidad,
    ### aleatorio, logaritmo, etc). y por cada n-grama hasta el máximo a observar.
    for var in variables:
        for cla in claves:
            for n in range(0, n_gram_max):
                df = agregar_columna_bd(df, f'{var}_{cla}: N_gram {n+1}', 0)
                df = agregar_columna_bd(df, f'log {var}_{cla}: N_gram {n+1}', np.nan)

    ### Añadimos los n-gramas correspondientes por nombre y por variable a analizar
    for rola in list(df.index):
        path_rand = os.path.join(mypath_rand, rola)
        for var in variables:
            files = []
            # Archivo probabilidades
            path = os.path.join(mypath_prob, var)
            files.append(os.path.join(path, f"{rola}.txt"))
            # Archivo Shuffle (o bootstrap)
            rand = "Bootstrap"
            path_var_rand = os.path.join(path_rand, var, rand, "Probabilidades")
            files.append(os.path.join(path_var_rand, f"{rand}_promedios.txt"))
            # Archivo aleatorios equiprobables
            rand = "Equiprobable"
            path_var_rand = os.path.join(path_rand, var, rand, "Probabilidades")
            files.append(os.path.join(path_var_rand, f"{rand}_promedios.txt"))
            ## añadimos n-gramas a un excel
            for cla, file in zip(claves, files):
                print(file)
                df = cargar_datos(rola, df, file, pressition, n_gram_max, f'{var}_{cla}')
    return df

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
##Rutas
ruta_py = os.path.dirname(os.path.abspath(__file__))
ruta_py = os.path.abspath(os.path.join(ruta_py, os.pardir))

mypath = os.path.join(ruta_py, "Base Datos") ## aquí busca el excel 
# mypath = "C:\\Users\\aleja\\Documents\\Artículos\\Música\\Giovanni"
# ruta probabilidades
mypath_prob = os.path.join(mypath,
                            "Probabilidades norep")

## carpeta donde guardamos aleatorios
mypath_rand = os.path.join(mypath,
                           'Aleatorios')
mypath_ngram = os.path.join(mypath,
                            "Ngramas norep")

# datos_canciones = "datos de canciones"  # Nombre de archivo
datos_canciones = "datos de canciones"  # Nombre de archivo
file_to_open = os.path.join(mypath,
                            datos_canciones + ".xlsx")  # Ruta completa

#####################################################################
n_gramas_gen = [1, 9] ### [N_grama inicial, N_grama final] que aparecerán en la gráfica que compara géneros
n_gramas_song = [1, 2, 3, 4, 5, 6, 7, 8, 9] ## tamaño de N_gramas que aparecerán en la gráfica por n_gramas por canción
n_gram_max = max(max(n_gramas_gen), max(n_gramas_song))
language = 'en'

################################################################################
ordenar = ['longitud', 'alfabeto'] ## sacarémos dos tipos de gráficas, ordenadas por longitud y aleatorio
analisis = ['Probabilidad', 'Logaritmo'] ## también haremos dos tipos por probabilidad y logaritmo
claves = ['pr', 'shff', 'eqp']

# Definimos las variables que vamos a graficar, se harán mezclas de ellas, por lo que conviene separar
var_musica = ['melodía', 'ritmo m', 'armonía'] #, 'mel no sil', 'armonía',
              # 'arm no sil']  # Variables relacionadas a la música
""" Opciones para var_musica (separar con comas):
'ritmo m' -> ritmo de la melodía, los tiempos de las notas
'ritmo a' -> ritmo de la armonía. Tiempos de los acordes
'melodía' -> melodía de la pieza, contando silencios como símbolo
'mel no sil' -> melodía de la pieza, sin contar silencios
'armonía' -> armonía de la pieza. Contando silencios
'arm no sil' -> armonía d ela pieza. Sin silencios """

var_intrinsecas = ['serie']  # Valores intrínsecos de los datos
""" Opciones para var_intrinsecas (separar con comas): 
'serie' -> la secuencia original de las de arriba
'D I' -> intervalo de diferencias (por ejemplo, la cantidad de notas que hay entre dos, con signo
         es decir, de do4 a re4 hay dos notas positivas. De re4 a do4 hay dos notas negativas
'U I' -> Intervalo de diferencias sin signo. (lo de arriba pero en valor absoluto).
'contour' -> Solo hay tres símbolos: -1, 0, 1. -1 sucede cuando hay una caida en el tono (o el tiempo)
             0 sucede cuando la nota anterior es igual (o el ritmo). 1 sucede cuando hay un aumento en el tono
'mod 12' -> unicamente aplicable a melodía. Devuelve la melodía en modulo 12. Vale lo mismo do4 que do3"""
variables = hacer_titulos(var_musica, var_intrinsecas)
# var_analisis = ['Probabilidad sin autocoincidencia', 'Desviación',
#                 'Hapax legonema', 'Frases distintas', 'Cantidad Frases']

pressition = '{0:.5f}'
### hacemos análisis y guardamos en excel o abrimos excel
carpeta_guardar = "Artículo 2"
carpeta_guardar = os.path.join(mypath, carpeta_guardar)
file = os.path.join(carpeta_guardar, "datos_graficas.xlsx")
new_analisis = True
if not os.path.isfile(file) or new_analisis:
    """ esto hará si new_analisis es verdadero o si no existe el archivo a graficar"""
    # Abrimos el documento con los datos que vamos a graficar/analizar
    df = pd.read_excel(file_to_open, sheet_name='Sheet1',
                       header=0)  # Abre datos en df
    df = agregar_columna_bd(df, "etiquetas_genero", np.nan) #creamos nueva columna de generos
    """tomaremos los subgeneros de las clásicas y géneros de blues y jazz. Esto se puede modificar
        si solo tomamos generos, poner [["Generos", ...]], si solo usamos subgeneros [["Subgenero", ...]]
        El caso en que de unas usemos géneros y subgeneros de otras es el que utilizamos abajo"""
    Generos_subgeneros = [["Genero", "Blues", "Jazz", "Rock", "Salsa"], ["Subgenero", "Clasica"]]
    [df, generos] = elegir_generos(df, Generos_subgeneros, language)
    
    df = df.set_index('Nombre') # para buscar por nombres
    # ESta función añadé indices de aleatorios y elige colores y marcadores-estilos de linea para
    # homologar gráficas
    df = generar_colores_marcadores(df, generos, claves)
    hacer_carpeta(carpeta_guardar)
    df = cargar_ngramas_random(df, variables, n_gram_max, mypath_prob,
                          mypath_rand, pressition, claves)
    df.to_excel(file)
else:
    # Abrimos el documento con los datos que vamos a graficar/analizar
    df = pd.read_excel(file, sheet_name='Sheet1',
                       header=0)
    df = df.set_index('Nombre')
    generos = df["etiquetas_genero"].explode().unique().tolist() ## estos son los generos finales
    for cla in claves:
        df[f"color {cla}"] = df[f"color {cla}"].map(eval)
        df[f"marcador {cla}"] = df[f"marcador {cla}"].map(string_tuple)

#######################################################
############ Para graficar ############################
# #######################################################

# eje_y = 'melodía serie'
# eje_x = eje_y + ' alfabeto'
# graf_ngrama(eje_x, eje_y, df, generos, claves, n_gramas_song)
# graf_ngrama_genero(eje_y, df, generos, claves, n_gramas_gen)
# plt.show()

# eje_y =  'ritmo m serie'
# eje_x = eje_y + ' alfabeto'
# graf_ngrama(eje_x, eje_y, df, generos, claves, n_gramas_song)
# graf_ngrama_genero(eje_y, df, generos, claves, n_gramas_gen)
# plt.show()

eje_y =  'ritmo m serie'
eje_x = eje_y + ' alfabeto'
graf_ngrama(eje_x, eje_y, df, generos, claves, n_gramas_song)
graf_ngrama_genero(eje_y, df, generos, claves, n_gramas_gen)
plt.show()
print("aqui")
