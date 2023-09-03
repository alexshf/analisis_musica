import codecs
import numpy as np
import os
import math
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from fractions import Fraction
import json
from deep_translator import GoogleTranslator # se instala en terminal con "pip install -U deep-translator"


def abrir_json(file):
    with open(file, "r") as fp:
        # Load the dictionary from the file
        datos = json.load(fp)
    return datos

def json_datos(path, nombre, datos): 
    ## guardamos los datos
    with open(os.path.join(path, f"{nombre}.txt"), "w") as fp:
        json.dump(datos, fp)  # encode dict into JSON
        
def abrir_datos(nombre):
    s = []
    f = codecs.open(nombre, "r", "latin-1")
    titulos = f.readline()
    titulos = titulos.split(", ")
    for x in f:
        linea = x.split(', ')
        s.append(linea)
    f.close
    dat = []
    for i in range(0, len(s)):
        for j in range(0, len(s[i])):
            try:
                dato = float(s[i][j])
            except:
                dato = Fraction(s[i][j])
            if not math.isnan(dato):
                if i == 0:
                    dat.append([dato])
                    titulos[j] = titulos[j].lstrip()
                else:
                    dat[j].append(dato)
    return [titulos, dat]


def txt_datos(datos, titulos, nombre_archivo, tamano):

    matriz_datos = np.empty(tamano, dtype='object')
    longitudes_titulos = []
    # creamos un array de la sere de datos con las series en las columnas. Agregamos nans en los espacios vacíos
    if not len(titulos) == 0:
        for j in range(0, len(titulos)):
            longitudes_titulos.append(len(titulos[j]))
            for k in range(0, tamano[0]):
                if k < len(datos[j]):
                    matriz_datos[k][j] = str(datos[j][k])
                else:
                    matriz_datos[k][j] = np.nan
        titulos_corregidos = []
        # creamos los titulos correspondientes, agregando espacios a la izquierda
        for j in range(0, len(titulos)):
            cadena = ''
            for k in range(0, max(longitudes_titulos)):
                if k < max(longitudes_titulos) - len(titulos[j]):
                    cadena = cadena + ' '
                else:
                    cadena = cadena + titulos[j][k - (max(longitudes_titulos) - len(titulos[j]))]
            titulos_corregidos.append(cadena)
            # Renglón de títulos de columnas
        columns = np.array(titulos_corregidos)[np.newaxis, :]
        with open(nombre_archivo, 'w') as file_txt:
            np.savetxt(file_txt, np.vstack((columns, matriz_datos)), delimiter=', ', fmt='%s')
    else:
        for k in range(0, tamano[0]):
            matriz_datos[k][0] = datos[k]
        with open(nombre_archivo, 'w') as file_txt:
            np.savetxt(file_txt, np.transpose(matriz_datos), delimiter=', ', fmt='%s')


def hacer_carpeta(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def agregar_columna_bd(df, columna_nueva, elemento):
    condicion = isinstance(elemento, np.ndarray) or \
                isinstance(elemento, tuple) or \
                isinstance(elemento, list)
    if condicion and len(elemento) == len(df):
        new_dat = elemento
    elif condicion:
        new_dat = np.empty(len(df), dtype=type(elemento))
        for i in range(0, len(new_dat)):
            new_dat[i] = elemento
    else:
        new_dat = np.empty(len(df), dtype=type(elemento))
        new_dat[:] = elemento
    df[columna_nueva] = new_dat
    return df


def elegir_generos(df, gens_subgens, language):
    cond = False
    for genero in gens_subgens:
        for j in range(1, len(genero)):
            generos = df["Genero"] == genero[j] # elige los géneros marcados
            cond = cond | generos # se hacen True los generos marcados
            df.loc[generos, "etiquetas_genero"] = \
                list(map(GoogleTranslator(source='auto', 
                                          target=language).translate,
                         df.loc[generos, genero[0]])) ## guardamos ya sea subgeneros o generos
    df = df[cond] ## aquí quitamos los que no son true
    df = df.sort_values(by=['Genero', 'Subgenero']) ## ordenamos

    generos = df["etiquetas_genero"].explode().unique().tolist() ## estos son los generos finales

    return [df, generos]


def normalizar_maximo_columna(datos):
    for i in range(0, len(datos)):
        if np.count_nonzero(~np.isnan(datos[i])) > 0:
            maximo = np.nanmax(datos[i])
            minimo = np.nanmin(datos[i])
            for j in range(0, len(datos[i])):
                if not np.isnan(datos[i][j]) and np.count_nonzero(~np.isnan(datos[i])) > 1:
                    datos[i][j] = (datos[i][j] - minimo) / (maximo - minimo)
                elif not np.isnan(datos[i][j]) and np.count_nonzero(~np.isnan(datos[i])) == 1:
                    datos[i][j] = 1
            del maximo, minimo
    return datos


def crear_tabla_ijmpc(descripcion, tit_columnas, datos, ultima_linea, etiqueta):
    tabla = "\\begin{table}[ht] \n \\tbl{"
    tabla += descripcion + '} \n {\\begin{tabular}{@{}'
    col = ''

    for i in range(0, len(tit_columnas[0][0])):
        for j in range(0, tit_columnas[0][0][i]):
            col += 'c'
        if tit_columnas[0][1][i] == 1:
            col += '|'
    tabla += col + '@{}} \\toprule \n'

    for j in range(0, len(tit_columnas)):
        if type(tit_columnas[j][0]) == list or type(tit_columnas[j][0]) == np.ndarray:
            for i in range(0, len(tit_columnas[j][-1])):
                if tit_columnas[j][0][i] != 1:
                    tabla += "\\multicolumn{" + str(tit_columnas[j][0][i]) + "}{c}{" + tit_columnas[j][-1][i] + "}"
                else:
                    tabla += tit_columnas[j][-1][i]
                if i + 1 < len(tit_columnas[j][-1]):
                    tabla += ' & '
        else:
            for i in range(0, len(tit_columnas[j])):
                tabla += tit_columnas[j][i]
                if i + 1 < len(tit_columnas[j]):
                    tabla += ' & '
        tabla += "\\" + "\\ \n"
    tabla += "\\colrule \n"
    for i in range(0, len(datos)):
        for j in range(0, len(datos[i])):
            if type(datos[i][j]) == str:
                tabla += datos[i][j]

            elif type(datos[i][j]) == list and type(datos[i][j][0]) != list:
                for k in range(0, len(datos[i][j])):
                    if type(datos[i][j][k]) == str:
                        tabla += datos[i][j][k]
                    else:
                        tabla += str(datos[i][j][k])
                    if k != len(datos[i][j]) - 1:
                        tabla += ', '
            elif type(datos[i][j]) == list and type(datos[i][j][0]) == list:
                tabla += "\\colrule \n"
                for r in range(0, len(datos[i][j][0])):
                    if datos[i][j][0][r] != 1:
                        tabla += "\\multicolumn{" + str(datos[i][j][0][r]) + "}{c}{" + datos[i][j][-1][r] + "}"
                    else:
                        tabla += datos[i][j][-1][r]
                    if r + 1 < len(datos[i][j][0]):
                        tabla += ' & '
                    else:
                        tabla += "\\colrule \n"

            else:
                tabla += str(datos[i][j])
            if j < len(datos[i])-1:
                tabla += ' & '
        tabla += "\\" + "\\ \n"

    tabla += "\\botrule \\" + "\\ \n"
    for i in range(0, len(ultima_linea)):
        tabla += "\\textbf{" + ultima_linea[i] + "} "
        if i < len(ultima_linea)-1:
            tabla += " & "
        else:
            tabla += "\\" + "\\ \n \\botrule \n"
    tabla +=  "\\end{tabular} \\label{" + etiqueta + "}} \n \\end{table}"

    print(tabla)


def separar_nombres(nombres, long):
    nombres_separados = []
    renglones = 0
    for i in range(0, len(nombres)):
        nombres_separados.append([''])
        str = nombres.iloc[i]
        split = str.split()
        ind = 0
        renglones += 1
        for j in split:
            if len(nombres_separados[i][ind] + j) < long:
                if j != split[0]:
                    nombres_separados[i][ind] += ' '
                nombres_separados[i][ind] += j
            else:
                nombres_separados[i].append(j)
                ind += 1
                renglones += 1

    return nombres_separados, renglones


def crear_tabla_latex(descripcion, tit_columnas, datos, ultima_linea, etiqueta):
    tabla = "\\begin{table}[h!] \n \centering \n \\begin{tabular}{|"
    col = ''

    for i in range(0, len(tit_columnas[0][0])):
        for j in range(0, tit_columnas[0][0][i]):
            col += 'c'
        if tit_columnas[0][1][i] == 1:
            col += '|'
    tabla += col + '|} \\hline \n'

    for j in range(0, len(tit_columnas)):
        if type(tit_columnas[j][0]) == list or type(tit_columnas[j][0]) == np.ndarray:
            for i in range(0, len(tit_columnas[j][-1])):
                if tit_columnas[j][0][i] != 1:
                    tabla += "\\multicolumn{" + str(tit_columnas[j][0][i]) + "}{c}{" + tit_columnas[j][-1][i] + "}"
                else:
                    tabla += tit_columnas[j][-1][i]
                if i + 1 < len(tit_columnas[j][-1]):
                    tabla += ' & '
        else:
            for i in range(0, len(tit_columnas[j])):
                tabla += tit_columnas[j][i]
                if i + 1 < len(tit_columnas[j]):
                    tabla += ' & '
        tabla += "\\" + "\\ \n"
    tabla += "\\hline \n"
    for i in range(0, len(datos)):
        for j in range(0, len(datos[i])):
            if type(datos[i][j]) == str:
                tabla += datos[i][j]

            elif type(datos[i][j]) == list and type(datos[i][j][0]) != list:
                for k in range(0, len(datos[i][j])):
                    if type(datos[i][j][k]) == str:
                        tabla += datos[i][j][k]
                    else:
                        tabla += str(datos[i][j][k])
                    if k != len(datos[i][j]) - 1:
                        tabla += ', '
            elif type(datos[i][j]) == list and type(datos[i][j][0]) == list:
                tabla += "\\hline \n"
                for r in range(0, len(datos[i][j][0])):
                    if datos[i][j][0][r] != 1:
                        tabla += "\\multicolumn{" + str(datos[i][j][0][r]) + "}{c}{" + datos[i][j][-1][r] + "}"
                    else:
                        tabla += datos[i][j][-1][r]
                    if r + 1 < len(datos[i][j][0]):
                        tabla += ' & '
                    else:
                        tabla += "\\hline \n"

            else:
                tabla += str(datos[i][j])
            if j < len(datos[i])-1:
                tabla += ' & '
        tabla += "\\" + "\\ \n"

    tabla += "\\hline \\" + "\\ \n"
    for i in range(0, len(ultima_linea)):
        tabla += "\\textbf{" + ultima_linea[i] + "} "
        if i < len(ultima_linea)-1:
            tabla += " & "
        else:
            tabla += "\\" + "\\ \n \\hline \n"
    tabla += "\\end{tabular} \n"
    tabla += '\\caption{' + descripcion + '}'
    tabla += "\\label{" + etiqueta + "} \n \\end{table}"

    print(tabla)


def generar_colores_marcadores(df, generos, claves):
    l = len(generos)
    color = poner_color(l)
    marcador = []
    estilo_linea = []
    h = 0
    for ind in range(0, l):
        marcador.append((3, 0, (360/(len(generos)-h))*ind))
        estilo_linea.append('dotted')


    colores = (np.nan, np.nan, np.nan)
    marca = colores
    agregar_columna_bd(df, f"color {claves[0]}", colores)
    agregar_columna_bd(df, f"marcador {claves[0]}", marca)
    agregar_columna_bd(df, f"linea {claves[0]}", estilo_linea[0])

    i=0
    for gen in generos:
        cond = df['etiquetas_genero'] == gen
        for ind in range(0, len(cond)):
            if cond[ind]== True:
                df.iat[ind,
                       df.columns.get_loc(f"color {claves[0]}")] = \
                        color.colors[i]
                df.iat[ind,
                       df.columns.get_loc(f"marcador {claves[0]}")] = \
                    marcador[i]
                df.iat[ind,
                       df.columns.get_loc(f"linea {claves[0]}")] = \
                    estilo_linea[i]
        i += 1

    shuff_col = (1, .2, 0, 0.5) ## el color característico de los shuffle
    agregar_columna_bd(df, f"color {claves[1]}", shuff_col)
    agregar_columna_bd(df, f"marcador {claves[1]}", 'o')
    agregar_columna_bd(df, f"linea {claves[1]}", 'dashdot')
    equip_col = (1, 0, 0, 0.7)  ## el color característico de los equiprobables
    agregar_columna_bd(df, f"color {claves[2]}", equip_col)
    agregar_columna_bd(df, f"marcador {claves[2]}", '.')
    agregar_columna_bd(df, f"linea {claves[2]}", 'solid')

    return df

def poner_color(len_generos):
    color = plt.get_cmap('Pastel1') ##Tomamos colores de esta paleta
    color2 = plt.get_cmap('Dark2') ##Tomamos colores de esta paleta

    ind = 0 ## un contador para saber si nos pasamos de distintos generos
    ind_col = 0 ## un contador para saber qué agarramos de las paletas de colores
    new_color = np.arange(0, len_generos, dtype=object) ## aquí guardamos colores
    while ind < len_generos: # si nos pasamos, cortamos
        new_color[ind] = color.colors[ind_col] ## guardamos un color de la primera paleta
        ind += 1 ##avanzamos en la cuenta
        if ind < len_generos: ## si todavía hay géneros, ponemos color
            new_color[ind] = color2.colors[ind_col] ## ponemos color de la segunda paleta
            ind += 1 # avanzamos cuenta
        else:
            break
        ind_col += 1 #avanzamos color
    newcmp = ListedColormap(new_color) # este es el colormap

    return newcmp


