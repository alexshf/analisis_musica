from os import walk
from procesar import procesar
from funciones_auxiliares import  json_datos, txt_datos, hacer_carpeta, agregar_columna_bd
from funciones_complejidad import aplicar_algoritmo
from funciones_aleatorios import calcular_aleatorios
from exceltopdf import uno_excel
import pandas as pd
import os.path
import math
import numpy as np
# from joblib import Parallel, delayed ## para procesar en paralelo
import time


### funciones para calcular probabildades
def calculo_probabilidades(titulos_dat, cancion_dat, nombre):
    probabilidades = []
    print("sehizo ", titulos_dat)
    
    ## buscamos los ngramas y las probabilidades de la canción
    [ngramas, probabilidades] = aplicar_algoritmo(cancion_dat)
    
    

    ## guardamos los datos
    carpeta = os.path.join(mypath_prob, titulos_dat)
    hacer_carpeta(carpeta)
    json_datos(carpeta, f"{nombre}", probabilidades)
    ## guardamos los ngramas
    carpeta = os.path.join(mypath_ngram, titulos_dat)
    hacer_carpeta(carpeta)
    json_datos(carpeta, f"{nombre}", ngramas)
     

def filter_new_or_empty(df):
    #Recopilamos las canciones en la base que no han sido analizadas
    # si tiempo no esta, entonces todas las canciones se analizarán
    if 'tiempo' in df.columns: # si tiempo existe, entonces solo analizamos las nan
        # quitmaos las columnas llenas y dejamos las vacías (con nans)
        rolas = df[list(map(lambda x: not (isinstance(x, str))
                                   and math.isnan(x),
                         df['tiempo']))]['Nombre']
    else:
        rolas = df['Nombre']
    rolas = rolas.values.tolist() ## solo dejamos los nombres de las canciones que faltan rellenar
    return rolas


def actualiza_bd(dato_nuevo, valor_dato):
    global df
    """"actualiza la bd"""
    if not dato_nuevo in columnas:
        df = agregar_columna_bd(df, dato_nuevo, np.nan)
    df.loc[rola, dato_nuevo] \
        = valor_dato


def cancion_to_num(rola1):
    ## globales que salen de aquí
    global rola, columnas, mypath_rand_song

    rola = rola1 # para poder enviar globalmente

    mypath_rand_song = os.path.join(mypath_rand, rola) #carpeta de aleatorios
    hacer_carpeta(mypath_rand_song)

    ## guardamos pdf (comentar si ya existe)
    # excel_to_pdf(rola, mypath_xlsx, mypath_pdf)

    # Buscamos el índice de la cancion tanto en el excel de base de datos,
    # como en la carpeta de archivos
    if rola+".xlsx" in files:
        indice = files.index(rola + ".xlsx")  ## encuentra el nombre de cada archivo en la base
        uno_excel(os.path.join(mypath_xlsx, rola+".xlsx"))
        datos_retorno = procesar(os.path.join(mypath_xlsx, files[indice])) #datos retorno tiene la partitura como números
        columnas = df.columns
        nombre = files[indice][:-5]
        print(nombre) # para ver el nombre del archivo que se está leyendo
        ## guardamos tiempo y longitud
        # list(map(actualiza_bd, datos_retorno[0][0], datos_retorno[0][1]))
        for titulos, datos in zip(datos_retorno[0][0], datos_retorno[0][1]):
            actualiza_bd(titulos, datos)
        ## guardamos tamaño con repetidos y sin de datos
        # list(map(actualiza_bd, datos_retorno[1][0], datos_retorno[1][1]))
        for titulos, datos in zip(datos_retorno[1][0], datos_retorno[1][1]):
            actualiza_bd(titulos, datos)
        ## guardamos datos de canciones como números.
        txt_datos(datos_retorno[2][1], datos_retorno[2][0],
                  os.path.join(mypath_data, rola + '_series.txt'),
                  (len(datos_retorno[2][1][0]), len(datos_retorno[2][0])))
        ## calculamos y guardamos las probabilidades de los n_gramas
        # list(map(calculo_probabilidades, datos_retorno[2][1], datos_retorno[2][0]))
        t = time.time()
        for titulos, datos in zip(datos_retorno[2][0], datos_retorno[2][1]):
            path_rand_song_sec = os.path.join(mypath_rand_song, titulos)
            hacer_carpeta(path_rand_song_sec)
            long_serie = int(df.loc[rola, titulos + ' longitud'])
            alfabeto = int(df.loc[rola, titulos + ' alfabeto'])
            calculo_probabilidades(titulos, datos, nombre)
            calcular_aleatorios(datos, long_serie, alfabeto, path_rand_song_sec)
        print(time.time() - t)
    else:
        print(f"No existe {rola} en la base de datos")

        

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                    PROGRAMA                          """
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
## variables globales que usaremos en funciones
global df, mypath_prob, mypath_data, files, resultados_analisis
global mypath_xlsx, mypath_pdf, mypath_rand, mypath_ngram

# cargamos la dirección de las partituras
# en mypath está el excel on nombres a analizar y los
# excel de las canciones
ruta_py = os.path.dirname(os.path.abspath(__file__))
ruta_py = os.path.abspath(os.path.join(ruta_py, os.pardir))

mypath = os.path.join(ruta_py, "Base Datos") ## aquí busca el excel
mypath_xlsx = os.path.join(mypath, "partituras xlsx norep") ## aquí están los excel de las canciones


# guardamos n-gramas aquí
mypath_ngram = os.path.join(mypath,
                            "Ngramas norep")
hacer_carpeta(mypath_ngram)


## crearemos un directorio en "Base de datos" que se llama
## probabilidades, esta carpeta contendrá el
# calculo de las funciones de distribución empírica de cada n-grama
mypath_prob = os.path.join(mypath,
                            "Probabilidades norep")
hacer_carpeta(mypath_prob)

## En esta carpeta guardamos las canciones convertidas a números
mypath_data = os.path.join(mypath,
                           'Base txt')
hacer_carpeta(mypath_data)

## carpeta donde guardamos pdfs
mypath_pdf = os.path.join(mypath,
                           'partituras pdf-midi')
hacer_carpeta(mypath_pdf)

## carpeta donde guardamos aleatorios
mypath_rand = os.path.join(mypath,
                           'Aleatorios')
hacer_carpeta(mypath_rand)


# Revisamos los archivos en el directorio de exceles
files = []
for (_, _, filenames) in walk(mypath_xlsx):
    files.extend(filenames)
    break

## nombres resultados
resultados_analisis = ['Probabilidad sin autocoincidencia',
                    'Desviación', 'Hapax',
                    'Frases distintas', 'Cantidad Frases']

# Abrimos el documento con los nombres de las canciones.
# Además aquí colocarémos la salida
datos_canciones = "datos de canciones"  # Nombre de archivo
file_to_open = os.path.join(mypath,
                            datos_canciones + ".xlsx")  # Ruta completa
df = pd.read_excel(file_to_open, sheet_name='Sheet1',
                   header=0)  # Abre datos en df

# Definimos las variables que vamos a utilizar, se harán mezclas de ellas, por lo que conviene separar
""" Vamos a extraer ritmo(tiempos) de melodía, ritmo de armonía, melodía contando silencios,
melodía sin contar silencios, armonía con silencios y armonía sin silencios.
De cada serie calculamos su probabilidad sin autocoincidencia, la 'desviación' sin autocoincidencia (midiendo 
la distancia entre dos notas como el número de notas entre ellas), El Hapax (la cardinalidad del conjunto
de n-gramas que hay de longitud n)"""

if "Unnamed: 0" in df.columns: ## eliminamos está columna que a veces sale por default
    del df["Unnamed: 0"]
# rolas = filter_new_or_empty(df) # filtramos dejando las canciones a analizar
rolas = df['Nombre'] ## si queremos que haga todo de nuevo
df = df.set_index('Nombre')

print(rolas)
t = time.time()
# list(map(cancion_to_num, rolas)) # es como un for
for c in rolas:    
    # if (not 'tiempo' in df.columns) or (np.isnan(df.loc[c,'tiempo'])):
    cancion_to_num(c)
                                   
# Parallel(n_jobs=4)(delayed(cancion_to_num)(rola) for rola in rolas) ##lo hace en paralelo, pero no guarda excel
print(time.time()-t) #tiempo del algoritmo

df.to_excel(os.path.join(mypath, "datos de canciones.xlsx")) #guarda datos de canciones como longitud y esas cosas