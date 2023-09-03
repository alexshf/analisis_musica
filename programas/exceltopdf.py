import pandas as pd
import os.path
import subprocess
from funciones_auxiliares import hacer_carpeta
from joblib import Parallel, delayed
import time
from tkinter.filedialog import askopenfilename
import sys

def excel_to_pdf(nombre, data_folder_in, data_folder_out):
    
    hacer_carpeta(data_folder_out) ## hace esta carpeta
    if ".xlsx" in nombre:
        nombre = nombre[0:-5]
    elif ".xls" in nombre:
        nombre = nombre[0:-4]
        
    file_to_open = os.path.join(data_folder_in, nombre + ".xlsx") ## abrimos este arhcivo
    df = pd.read_excel(file_to_open, sheet_name='Hoja1') ## datos de la canción
    renglones = len(df) #máxima  longitud de las columnas

    partitura = "\\version \"2.18.2\"" + "\n" + \
                '\\sourcefileline 1164 \n \\layout { \\context { ' \
                '\\name ImproVoice \\type "Engraver_group" \\consists' \
                ' "Note_heads_engraver" \\consists "Rhythmic_column_engraver" ' \
                ' \\consists "Text_engraver" \\consists "Pitch_squash_engraver" ' \
                'squashedPosition = #0 \\override NoteHead.style = #\'slash' \
                ' \\alias Voice } \\context { \\Staff \\accepts "ImproVoice" }} ' \
                '\n melody= \n ' ## indispensable para lilypond

    ### el siguiente for concatena las cosas que queremos para la melodía de lilypond
    for i in range(0, renglones):
        for j in range(0, 4):
            if not df.isnull()[df.columns[j]][i]:
                if j == 3:
                    partitura += " " + df[df.columns[j]][i] + " "
                elif j == 1:
                    partitura += str(int(float(df[df.columns[j]][i])))
                else:
                    partitura += df[df.columns[j]][i]
            if df.isnull()[df.columns[j]][i] and j == 3:
                partitura += " "

    #Lo mismo pero para acordes
    chords = "acordes = \\chordmode{"

    columnas = len(df.columns)
    for i in range(0, renglones):
        for j in range(4, columnas):
            if not df.isnull()[df.columns[j]][i]:
                if j == 7:
                    chords += df[df.columns[j]][i] + " "
                elif j == 5:
                    chords += str(int(float(df[df.columns[j]][i])))
                elif j == 8:
                    chords += df[df.columns[j]][i] + " "
                else:
                    chords += df[df.columns[j]][i]
            if df.isnull()[df.columns[j]][i] and j == 7:
                chords += " "

    # finalizamos  lo de lilypond
    chords += "}"
    partitura += "}" + "\n" + chords + "\n \\score { \n << \n \\new StaffGroup = \"partitura\" << \n"
    partitura += " \\new ChordNames = \"acordes\" \\acordes \n \set chordChanges = ##t"
    partitura += " \\new Staff \\with {midiInstrument = #\"acoustic grand\"} \\melody >>\n>>"
    partitura += " \\layout{ } \\midi{ \\tempo 4 = 85}}"

    ######## guardamos el archivo
    file_salida = os.path.join(data_folder_out, nombre + ".ly")
    file = open(file_salida, "w")
    file.write(partitura)
    file.close()

    ##### corremos lilypond para generar el pdf del archivo automáticamente
    ##### si no sabes donde está tu programa lilypond comentalo y hazlo manual
    os.chdir(data_folder_out)
    #################################################################################################
    #################################################################################################
    ########### ANTES DE DESCOMENTAR; CAMBIAR LA RUTA LILYPOND
   
    #ruta_lilypond = "[RUTA LILIPOND]\\bin\\lilypond.exe"
    #subprocess.run([ruta_lilypond, "--pdf", file_salida])
    
    ################################################################################################
    ###############################################################################################
    
    ruta_py = os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.join(data_folder_out, os.pardir)),os.pardir)), 'programas')
    os.chdir(ruta_py)
    
def todos_excel():
    ####################################################################################
    ####################################################################################
    ####################################################################################
    """ Aquí comienza el programa que aplica la conversión a pdf de todas las canciones
    en la carpena del genero dado"""
    ################ Si solo quieres una canción, comentar esto (ctrl + /)y descomentar lo de abajo
    if getattr(sys, 'frozen', False):
        # The application is frozen
        ruta_py1 = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        ruta_py1 = os.path.dirname(os.path.abspath(__file__))
    
    ruta_py = os.path.abspath(os.path.join(ruta_py1, os.pardir))
    
    data_folder_in = os.path.join(ruta_py, "partituras xlsx norep")
    data_folder_out = os.path.join(ruta_py, "partituras pdf-midi")


    datos_canciones = "datos de canciones"  # Nombre de archivo
    file_to_open = os.path.join(data_folder_in,
                                datos_canciones + ".xlsx")  # Ruta completa
    df = pd.read_excel(file_to_open, sheet_name='Sheet1',
                       header=0)  # Abre nombres del excel que se van a convertir
    t = time.time()
    Parallel(n_jobs=4)(delayed(excel_to_pdf)(nombre, data_folder_in, data_folder_out)
                       for nombre in df['Nombre']) #en paralelo hace esto
    print(time.time()-t)
    os.chdir(ruta_py1)

def uno_excel(filename = None):
    ########################################################################
    ########################## ################################################
    # PAra una sola canción  #########
    ####################################################################
    ###################################################################
    if getattr(sys, 'frozen', False):
        # The application is frozen
        ruta_py1 = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        ruta_py1 = os.path.dirname(os.path.abspath(__file__))
    os.chdir(ruta_py1)

    if not filename:
        filename = askopenfilename()
    ## ruta donde está el excel de la canción
    ruta = os.path.dirname(filename)
    
    ## Nombre de la canción
    nombre =  filename[len(ruta)+1:]
    ## de salida, puede no existir la carpeta final (o sea "partituras pdf-midi", lo demás
    ## sí debe existir (hasta Base datos en este caso)
    ruta_py = os.path.abspath(os.path.join(ruta, os.pardir))
    
    ruta_salida_pdf =  os.path.join(ruta_py, "partituras pdf-midi")

    excel_to_pdf(nombre, ruta, ruta_salida_pdf)