# Analisis musical

Proyecto cuyos resultados se encuentran publicados en el artículo "Hernández-Fuentes, A., del Castillo-Mussot, M., &amp; Hernández-Gómez, C. (2021). High n-gram occurrence probability in baroque, classical and romantic melodies. International Journal of Modern Physics C, 32(02), 2150023." [link-artículo](https://www.worldscientific.com/doi/10.1142/S0129183121500236).

La carpeta [programas](https://github.com/alexshf/analisis_musica/tree/main/programas) contiene diversos scripts que nos permiten cargar, calcular probabilidades, crear datos aleatorios para comparación, analizar y graficar los datos deseados. Primeramente, debemos transcribir manualmente (por ahora) partituras. Esta transcripción se realiza con la sintaxis utilizada en el proyecto GNU [LilyPond](https://lilypond.org/). Esta sintaxis debe guardarse en un excel con cierta estructura en la carpeta [partituras xlsx norep](https://github.com/alexshf/analisis_musica/tree/main/Base%20datos/partituras%20xlsx%20norep). Un ejemplo se encuentra en dicha carpeta: [Air on the g string.xlsx](https://github.com/alexshf/analisis_musica/blob/main/Base%20datos/partituras%20xlsx%20norep/Air%20on%20the%20g%20string.xlsx). Algunos detalles de este archivo deben colocarse en otro excel en la carpeta [Base datos](https://github.com/alexshf/analisis_musica/tree/main/Base%20datos). Este excel se llama [datos de canciones.xlsx](https://github.com/alexshf/analisis_musica/blob/main/Base%20datos/datos%20de%20canciones.xlsx).


## [calcular_probabilidades.py](https://github.com/alexshf/analisis_musica/blob/main/programas/calcular_probabilidades.py)

Este script se divide en programas para realizar tres acciones indispensables:

- **Carga e interpretación de datos**. Por un lado, junta las partes que se cargaron en el excel de la partitura y crea el archivo .ly de LilyPond, para visualizar un pdf de la partitura. Por otro lado, interpreta todos los simbolos y se cambian por números naturales para facilitar operaciones.
- **Cálculo de Parámetros**. Realiza el cálculo de todos los parámetros indispensables para el análisis. Estos datos son guardados en archivos de texto para no volver a ser calculados al momento de realizar el análisis y la interpretación de los datos.
- **Creación de Aleatorios**. Para la comparación de resultados, creamos dos tipos de datos aleatorios. Uno partiendo de la idea de que los símbolos son equiprobables y otra pensando que los símbolos tienen la misma distribución pero fueron colocados de forma aleatoria (permutación aleatoria).

Para estas tareas, se llamaran distintas funciones de otros archivos que se encuentran en la misma carpeta.

## [analisis probabilidades.py](https://github.com/alexshf/analisis_musica/blob/main/programas/analisis%20probabilidades.py)

Este script se divide en programas para realizar dos acciones indispensables:

- **Pruebas estadísticas**. Los parámetros calculados anteriormente nos permiten realizar distintas pruebas de ajustes, revisar tendencias y diferencias por géneros musicales y comparar con sus respectivos datos creados aleatoriamente.

- **Gráficar**. Realizamos gráficas acorde a lo que sea de interés en las pruebas estadísticas.



-----------------------------------------------------------------------------------------------------------------------------------------------



