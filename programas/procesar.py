import pandas as pd
from fractions import Fraction

""" Aquí colocaremos una serie de funciones que nos ayudaran a crear las series que serán analizadas con los
algoritmos de complejidad correspondientes. """

def procesar(excel):
    """ Comenzamps abriendo el archivo correspondiente a análisis, guardado en el nombre 'excel'. Luego,
    definimos las variables de salida. En este caso queremos que salgan todas las series unidimensionales a las cuales
    les aplicaremos los algoritmos."""

    df = pd.read_excel(excel, sheet_name='Hoja1') ## Leemos el excel con nombres de partituras
    
    
    # variables principales que se regresan. Apartir de ellas construimos las demás
    ritmo = [] # tiempos que duran las notas. Se unen ligaduras
    rit_arm = [] # tiempos que duran las armonías, se cuenta una cada que cambia de acorde o de comppas con el mismo acorde
    melodia = [] # asociamos números a melodía por conveniencia (no afectan el resultado pues al final solo contamos repeticiones)
    melodia_sin_silencios = [] # misma que anterior sin considerar silencios
    acorde = [] # asociamos números a acordes con orden- 1ra, 3ra(2da o 4ta), 5ta(aug o dim), etc..
    acorde_sin_silencios = [] # acordes sin los N.C.
    acorde_triada = [] # Vectores acordes
    acorde_comp = [] #
    tonalidad = [] # Armadura, aquí se guardarán todas las que hay.
    tiempo = [] # El tiempo de la pieza (no rpm), 3/4, 4/4, etc

    # Resumimos la condición inicial en una variable
    cond_ini = df[df.columns[0]][0]
    # Solo leeremos los archivos que tengan de inicio '\key', así controlamos que no se lean otro tipo de archivos.
    if "\key" in cond_ini:
        # Condicionales ritmo melodía. Nos sirven para modificar los tiempos de acuerdo a la captura en formato lilypond
        # Algunas piezas comienzan con tresillos. Ésta instrucción revisa si eso sucede y cambia los tiempos.
        if (not pd.isnull(df[df.columns[3]][0])) \
                and isinstance(df[df.columns[3]][0], str) \
                and "\\tuplet" in df[df.columns[3]][0]:
            rit_change = buscar_tuplet_time(df[df.columns[3]][0], "tuplet")  # se multiplica por el valor buscado si
            # es un tresillo (u otra variación en el tiempo)
        else:
            rit_change = 1  # Multiplica por 1 en otro caso (no hay variación del tiempo)

        rit_plus = 0  # Condicional que determina cuándo hay ligaduras en el ritmo de la melodía
        # condicionales ritmo armonía, lo mismo que el ritmo melodía
        if len(df.columns) >= 9 \
                and (not pd.isnull(df[df.columns[8]][0])) \
                and "\\tuplet" in df[df.columns[8]][0]:
            rit_arm_change = buscar_tuplet_time(df[df.columns[8]][0], "tuplet")
        else:
            rit_arm_change = 1
        rit_arm_plus = 0 # Condicional que determina cuándo hay ligaduras en el ritmo de la armonía

        # variables de tempo y armadura. Incialmente siempre deben existir. Además, pueden cambiar durante la pieza
        tiempo = buscar_tuplet_time(cond_ini, "time") # ya sea 4/4 o 3/4 etc
        tonalidad = buscar_tonalidad(cond_ini) # luego de \key se  muestra la tonalidad
        """ Ahora comenzarémos a construir las series"""
        for i in range(1, df.shape[0]):
            # condicionales que se usarán para modificar variables (tresillos, ligaduras, puntillos, etc)
            cond_mel = df[df.columns[3]][i] ## con esto notamos si hay ligaduras o tresillos u otras cosas
            cond_rit = df[df.columns[2]][i] ## Con esto notamos si hay puntillos
            rit_orig = Fraction(1, int(df[df.columns[1]][i])) ## lilypond toma los tiempos como 1/tiempo

            # para ritmos los puntillos suman la mitad del valor y a veces también un cuarto
            if pd.isnull(cond_rit):
                rit_plus = 0
            elif "." in cond_rit:
                div = 2
                rit_plus = 0
                for _ in range(0, len(cond_rit)):
                    rit_plus += Fraction(rit_orig, div)
                    div += 2

            # sumamos tiempos en ligaduras o se cambia el tiempo y las notas de la melodía
            # para melodías necesitamos cambiar los símbolos a números y juntar los que se enlazan con ligaduras
            if not pd.isnull(cond_mel):
                if "\\)" in cond_mel: #busca cerradura de ligadura
                    ritmo[-1] = ritmo[-1] + ((rit_orig + rit_plus) * rit_change)
                elif "ImproVoice{" in cond_mel: # No cuento melodía que son rasgueos (?)
                    ritmo.extend([(rit_orig + rit_plus) * rit_change])
                else: #no hay ligadura
                    n = nota_en_numero(df[df.columns[0]][i]) # función que cambia notas a números para fácil manejo de bemoles y sostenidos
                    melodia.extend([n])
                    ritmo.extend([(rit_orig + rit_plus) * rit_change])
                    if not n == -25: #si no es silencio (los silencios se "llaman" "-25"
                        melodia_sin_silencios.extend([n])

                # los tresillos cambian el valor del ritmo
                if "\\tuplet" in cond_mel:
                    rit_change = buscar_tuplet_time(cond_mel, "tuplet")
                elif "}" in cond_mel:
                    rit_change = 1

                # agregar tiempos si hay
                if "\\time" in cond_mel:
                    tiempo = tiempo + ", " + buscar_tuplet_time(cond_mel, "time")

                # agregar modos(armadura) si hay
                if "\key" in cond_mel:
                    tonalidad = tonalidad + ", " + buscar_tonalidad(cond_mel)
            else:
                # Usamos una función auxiliar para modificar las notas por números, siendo el do central 0.
                n = nota_en_numero(df[df.columns[0]][i])
                melodia.extend([n])
                ritmo.extend([(rit_orig + rit_plus) * rit_change])
                if not n == -25:
                    melodia_sin_silencios.extend([n])

            """ Aquí comenzamos a buscar lo correspondiente a acordes-armonías"""
            # condicionales armonías
            # condicionales que se usan para modificar variables
            if not pd.isnull(df[df.columns[4]][i]):
                nota_base = df[df.columns[4]][i]
                rit_arm_orig = Fraction(1, int(df[df.columns[5]][i]))
                if len(df.columns) >= 7:
                    cond_rit_arm = df[df.columns[6]][i]
                else:
                    cond_rit_arm = []

                # para ritmos los puntillos suman la mitad del valor y a veces también un cuarto acorde
                if pd.isnull(cond_rit_arm):
                    rit_arm_plus = 0
                elif "." in cond_rit_arm:
                    rit_arm_plus = 0
                    div_a = 2
                    for _ in range(0, len(cond_rit_arm)):
                        rit_arm_plus += Fraction(rit_arm_orig, div_a)
                        div_a += 2

                # convierte acordes en array de números
                if not pd.isnull(nota_base):
                    rit_arm.append((rit_arm_orig + rit_arm_plus) * rit_arm_change)
                    if len(df.columns) >= 8:
                        modif = df[df.columns[7]][i]
                    else:
                        modif = []
                    if "r" == nota_base:
                        acorde.extend([-25])
                        acorde_triada.append([-25])
                        acorde_comp.append(1)
                    else:
                        # usamos una función auxiliar para determinar los datos de una triada (o acorde)
                        basico = acorde_basica(nota_base, modif)
                        acorde.extend(basico)
                        acorde_sin_silencios.extend(basico)
                        acorde_triada.append(basico)
                        acorde_comp.append(len(basico))
                # os tresillos cambian el valor del ritmo de la acorde
                if len(df.columns) >= 9 and not (pd.isnull(df[df.columns[8]][i])):
                    if "\\tuplet" in df[df.columns[8]][i]:
                        rit_arm_change = buscar_tuplet_time(df[df.columns[8]][i], "tuplet")
                    elif "}" in df[df.columns[8]][i]:
                        rit_arm_change = 1
    else:
        print(f"Esta canción: {excel} no tiene key en donde debería. Revisar")

    """Hasta aquí tenemos ya el ritmo melódico, ritmo armónico, melodía y acordes como datos. Aquí creamos
    solo una matriz de salida de dos dimensiones con dimensiones propias dentro. La primera dimensión, correspondiente
    a las longitudes, y la segunda a las series."""

    var_musica = ['ritmo m', 'ritmo a', 'melodía', 'mel no sil', 'armonía',
                  'arm no sil']  # Variables relacionadas a la música
    var_intrinsecas = ['serie']  # Valores intrínsecos de los datos

    titulos = hacer_titulos(var_musica, var_intrinsecas)


    # primero definimos la serie armonía
    # armonia = serie_armonia(acorde, acorde_triada)

    if acorde_sin_silencios == []:
        acorde_sin_silencios = acorde
        
    matriz_series = [ritmo, rit_arm, melodia, melodia_sin_silencios, acorde, acorde_sin_silencios]
    # # Construimos un vector de las series de salida, con sus títulos correspondientes
    # matriz_series = calcular_series(ritmo, var_musica[0])
    # m = calcular_series(rit_arm, var_musica[1])
    # matriz_series.extend(m)
    # del m
    # m = calcular_series(melodia, var_musica[2])
    # matriz_series.extend(m)
    # del m
    # m = calcular_series(melodia_sin_silencios, var_musica[3])
    # matriz_series.extend(m)
    # del m
    # m = calcular_series(acorde, var_musica[4])
    # matriz_series.extend(m)
    # del m
    # m = calcular_series(acorde_sin_silencios, var_musica[5])
    # matriz_series.extend(m)
    # del m
    # titulos.append('long acorde')
    # matriz_series.append(acorde_comp)
    # creamos los valores de las longitudes y el alfabeto de cada serie de datos.
    longitudes = []
    titulos_long = []

    for k in range(0, len(matriz_series)):
        l_t = len(matriz_series[k])
        l_sr = eliminar_repetidos(matriz_series[k], 'longitud')
        ti_l_t = titulos[k] + ' longitud'
        ti_l_sr = titulos[k] + ' alfabeto'
        longitudes.extend([l_t, l_sr])
        titulos_long.extend([ti_l_t, ti_l_sr])

    return [[['tiempo', 'tonalidad'], [tiempo, tonalidad]], [titulos_long, longitudes], [titulos, matriz_series]]



#  ------------------------------------------- Armonía
def serie_armonia(acorde, triada):
    """ Cambiaremos la estructura de acordes para obtener una menor entropía (ya que no importa para la armonía
    la posición en que se coloquen. Idealmente debemos organizar a partir de la fund tonica-tercera-quinta como triada
    principal. Sin embargo, al desconocer esto, vamos a organizar de acuerdo a las triadas: Se más-repetido-medio rep-
    menos-rep. De esta forma alcanzarémos una menor entropía. Además, seguramente coincidirá con la estructura modal
    correspondiente."""
    armonia = reordenar_max(acorde, triada[0])
    for i in range(1, len(triada)):
        armonia.extend(reordenar_max(acorde, triada[i]))
    return armonia


def reordenar_max(serie, orden_orig):
    """ Esta funcuón reordena de acuerdo con la máxima repetición de la nota dentro del acorde correspondiente"""
    reorden = []
    indicadores = []
    for i in range(0, len(orden_orig)):
        indicadores.append(serie.count(orden_orig[i]))
    for i in range(0, len(orden_orig)-1):
        reorden.append(orden_orig[indicadores.index(max(indicadores))])
        del orden_orig[indicadores.index(max(indicadores))]
        del indicadores[indicadores.index(max(indicadores))]
    reorden.append(orden_orig[0])
    return reorden
# ------------------------------------------


def calcular_series(serie, var_music):
    """Calculamos las series de la resta, la resta con valor absoluto, si cambió o no y el modulo solo para melodía"""
    d_i = []
    u_i = []
    contour = []
    mod_12 = []
    for i in range(0, len(serie) - 1):
        if serie[i] == -25 and serie[i + 1] == -25:
            d_i.append(0)
        elif serie[i] == -25:
            d_i.append(50)
        elif serie[i + 1] == -25:
            d_i.append(-50)
        else:
            d_i.append(serie[i + 1] - serie[i])  # D i son los intervalos directos
        u_i.append(abs(d_i[i]))  # D i son los intervalos indirectos
        # Contour nos marca cuándo aumentó y cuándo disminuyó el intervalo.
        if serie[i + 1] - serie[i] > 0:
            contour.append(1)
        elif serie[i + 1] - serie[i] < 0:
            contour.append(-1)
        else:
            contour.append(0)

    # La melodía tendrá la misma melodía modulo 12
    if var_music == "melodía" or var_music == "mel no sil":
        for i in range(0, len(serie) - 1):
            if serie[i] == -25:
                mod_12.append(-25)
            else:
                mod_12.append(serie[i] % 12)
        series_salida = [serie, d_i, u_i, contour, mod_12]
    else:
        series_salida = [serie, d_i, u_i, contour]

    return series_salida


def hacer_titulos(var_music, var_intrinsecas):
    titulos = []
    # crear títulos de las seruies
    for var_musica in var_music:
        for i in range(0, len(var_intrinsecas)):
            if not "mod" in var_intrinsecas[i]:
                titulos.append(var_musica + ' ' + var_intrinsecas[i])
            elif var_musica == 'melodía' or var_musica == "mel no sil":
                titulos.append(var_musica + ' ' + var_intrinsecas[i])
    # Solo la melodía tendrá un módulo 12 para análisis

    return titulos


def buscar_tonalidad(cond_ini):
    """ Nos regresa la armadura (solo ponemos mayor, pero podríamos ser más específicos)"""
    h = cond_ini.index("\key") + 5
    k = cond_ini.index("\m") - 1
    nota_central = cond_ini[h:k]
    tonalidad = []
    if "\major" in cond_ini:
        tonalidad = "Mayor"
    elif "\minor" in cond_ini:
        tonalidad = "minor"
    if "es" in nota_central:
        nota_central = nota_central[0] + " bemol"
    elif "is" in nota_central:
        nota_central = nota_central[0] + "sostenido"
    key = nota_central + " " + tonalidad
    return key


def nota_en_numero(nota):
    """Asociamos un número a las notas. Sirve para poder cambiar sostenidos y bemoles más que nada. Esto para las
    12 notas básicas (do-si). Luego movemos la escala"""
    valor_nota = []
    if "c" in nota:
        valor_nota = 0
    elif "d" in nota:
        valor_nota = 2
    elif "e" in nota and "es" not in nota:
        valor_nota = 4
    elif "ees" in nota:
        valor_nota = 4
    elif "f" in nota:
        valor_nota = 5
    elif "g" in nota:
        valor_nota = 7
    elif "a" in nota:
        valor_nota = 9
    elif "b" in nota:
        valor_nota = 11
    elif "r" in nota:
        valor_nota = -25
    valor_nota += nota.count("is") # Añadimos un número por cada sostenido (a veces hay más de uno)
    valor_nota -= nota.count("es") # Añadimos un número por cada bemol (a veces hay más de uno)
    valor_nota += nota.count("'") * 12 # Se mueve la escala
    valor_nota -= nota.count(",") * 12 # Se mueve la escala
    return valor_nota


def buscar_tuplet_time(cadena, codigo):
    """Buscamos las variaciones de tiempo (tresillos y esas cosas) y también si cambia el tiempo de la pieza"""
    index_list = []
    del index_list[:]
    for i, x in enumerate(cadena):
        if x.isdigit():
            index_list.append(x)
    denominador = int(index_list[0])
    numerador = int(index_list[1])
    numero = []
    if codigo == "tuplet":
        numero = Fraction(numerador, denominador)
    elif codigo == "time":
        numero = str(denominador) + "/" + str(numerador)
    return numero


def acorde_basica(nota_base, modif):
    """Este espacio es para modificar los acordes con los modificadores correspondientes. Partimos de un acorde
    básico (do mi sol) = [0, 4, 7] y modificamos de acuerdo al nombre o los modificadores comunes de lilypond """
    acorde = [0, 4, 7]

    if pd.isnull(modif):
        acorde = acorde
    else:
        if "dim" in modif:
            acorde[1] = 3
            acorde[2] = 6
        elif "m" in modif:
            acorde[1] = 3

        if "2" in modif:
            acorde[1] = 2

        if "3-" in modif:
            acorde[1] = 3
        elif "3+" in modif:
            acorde[1] = 5
        elif "3" in modif and "^3" not in modif:
            acorde[1] = 4

        if "5-" in modif:
            acorde[2] = 6
        elif "5+" in modif or "aug" in modif:
            acorde[2] = 8
        elif "5" in modif and "^5" not in modif:
            acorde[2] = 7

        if "6-" in modif:
            acorde.append(8)
        elif "6+" in modif:
            acorde.append(10)
        elif "6" in modif:
            acorde.append(9)

        if "7-" in modif:
            acorde.append(9)
        elif "7+" in modif or "maj7" in modif or "maj" in modif:
            acorde.append(11)
        elif "7" in modif and "^7" not in modif:
            acorde.append(10)

        if "8-" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(11)
            else:
                acorde.append(11)
        elif "8+" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(1)
            else:
                acorde.append(1)
        elif "8" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(0)
            else:
                acorde.append(0)

        if "9-" in modif:
            if not (10 in acorde or 11 in acorde):
                acorde.append(10)
                acorde.append(1)
            else:
                acorde.append(1)
        elif "9+" in modif:
            if not (10 in acorde or 11 in acorde):
                acorde.append(10)
                acorde.append(3)
            else:
                acorde.append(3)
        elif "9" in modif and "^9" not in modif:
            if not (10 in acorde or 11 in acorde):
                acorde.append(10)
                acorde.append(2)
            else:
                acorde.append(2)

        if "10-" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(3)
            elif len(acorde) == 4:
                acorde.append(2)
                acorde.append(3)
            else:
                acorde.append(3)
        elif "10+" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(5)
            elif len(acorde) == 4:
                acorde.append(2)
                acorde.append(5)
            else:
                acorde.append(5)
        elif "10" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(4)
            elif len(acorde) == 4:
                acorde.append(2)
                acorde.append(4)
            else:
                acorde.append(4)

        if "11-" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(4)
            elif len(acorde) == 4:
                acorde.append(2)
                acorde.append(4)
            else:
                acorde.append(4)
        elif "11+" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(6)
            elif len(acorde) == 4:
                acorde.append(2)
                acorde.append(6)
            else:
                acorde.append(6)
        elif "11" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(5)
            elif len(acorde) == 4:
                acorde.append(2)
                acorde.append(5)
            else:
                acorde.append(5)

        if "13-" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(8)
            else:
                acorde.append(8)
        elif "13+" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(10)
            else:
                acorde.append(10)
        elif "13" in modif:
            if len(acorde) < 4:
                acorde.append(10)
                acorde.append(2)
                acorde.append(9)
            else:
                acorde.append(9)

        if "sus2" in modif:
            acorde[1] = 2
        elif "sus4" in modif:
            acorde[1] = 5
        elif "sus" in modif:
            del acorde[1]

        if "^3" in modif:
            del acorde[1]
        if "^5" in modif:
            del acorde[2]
        if "^7" in modif:
            del acorde[3]
        if "^9" in modif:
            del acorde[4]

    numero = nota_en_numero(nota_base) # Como comenzamos con un acorde básico, ahora lo "movemos" a donde se "debe"
    for i in range(0, len(acorde)):
        acorde[i] += numero % 12

    # Si hay una inversión o se agrega una nota, se modifica el acorde, sino, pues no.
    if pd.notnull(modif) and "/" in modif:
        variante = nota_en_numero(modif)
        acorde_final = variar_acorde(acorde, variante)
    else:
        acorde_final = acorde

    return acorde_final


def variar_acorde(acorde, variante):
    """Para inversiones o añadir una nota de bajo"""
    acorde_final = []
    if variante in acorde:
        ind = acorde.index(variante)
        for i in range(0, len(acorde)):
            acorde_final.append(acorde[(ind + i) % len(acorde)])
    else:
        acorde_final.append(variante)
        acorde_final.extend(acorde)
    return acorde_final


def eliminar_repetidos(lista, salida):
    """ Función para eliminar repeticiones para un tipo de dato"""
    new_lista = [lista[0]]
    for i in range(1, len(lista)):
        if (not pd.isnull(lista[i])) and (not lista[i] in new_lista):
            new_lista.append(lista[i])
    if salida == 'datos':
        datos_salida = new_lista
    elif salida == 'longitud':
        datos_salida = len(new_lista)
    else:
        datos_salida = []
    return datos_salida






