# Music Tempo Analysis for Running Performance

## Descripción del proyecto

Este proyecto analiza la relación entre el tempo musical medido en BPM (beats per minute) y la cadencia de corredores medida en pasos por minuto (SPM). El objetivo es identificar si ciertos rangos de BPM pueden servir como referencia para seleccionar música durante entrenamientos de running.

## Problema

Durante los entrenamientos de running, la música suele seleccionarse principalmente por preferencias personales, sin considerar cómo sus características pueden influir en el ritmo de carrera. El tempo musical medido en BPM podría estar relacionado con la cadencia del corredor, pero esta relación no siempre es considerada al momento de elegir música para entrenar.

## Pregunta de investigación

¿Existe una relación entre el BPM de la música y la cadencia de los corredores medida en pasos por minuto (SPM), y qué rangos de BPM podrían servir como referencia para seleccionar canciones durante entrenamientos de running?

## Usuario e interesado

El principal usuario de este análisis son corredores recreativos, entrenadores deportivos y aplicaciones enfocadas en entrenamiento físico.

Este análisis puede ayudar a tomar decisiones sobre la selección de música para entrenamientos, utilizando rangos de BPM asociados con diferentes niveles de cadencia.

## Fuentes de datos

Para realizar el análisis se utilizaron dos fuentes principales de datos:

### Dataset de Spotify

El primer dataset contiene información de canciones y sus características musicales. Las variables utilizadas principalmente fueron el tempo medido en BPM (beats per minute) y otras características descriptivas de las canciones.

Este dataset permitió analizar la disponibilidad de canciones dentro de diferentes rangos de BPM que podrían relacionarse con distintos ritmos de entrenamiento.

### Dataset de corredores

El segundo dataset corresponde a un experimento con corredores donde se registró la relación entre la música utilizada y la cadencia de los participantes.

Las principales variables utilizadas fueron:

- BPM promedio de la música (`bpm_avg`)
- Cadencia promedio del corredor (`spm_avg`)
- Condición experimental (`condition`)

Este dataset permitió estudiar si existe una relación entre el tempo musical y la cadencia de carrera.

## Metodología

El análisis se desarrolló siguiendo las siguientes etapas:

1. **Carga de datos**
   
   Se importaron los datasets utilizando Python y librerías de análisis de datos como Pandas.

2. **Exploración inicial**

   Se revisó la estructura de los datos mediante dimensiones, tipos de variables, valores faltantes y estadísticas descriptivas.

3. **Limpieza de datos**

   Se eliminaron registros inválidos y valores que podían afectar el análisis. En el dataset de corredores se descartaron observaciones donde el BPM promedio tenía valores no válidos (-1), evitando afectar los cálculos de correlación y promedios.

4. **Análisis exploratorio**

   Se analizaron distribuciones de BPM, estadísticas de cadencia y la relación entre ambas variables mediante correlación.

5. **Integración de datasets**

 Los datasets fueron comparados utilizando rangos de BPM para analizar si la disponibilidad de canciones en Spotify coincide con los rangos de tempo asociados con mayores valores de cadencia.

6. **Visualización**

   Se generaron gráficas para identificar patrones entre el tempo musical y la cadencia de los corredores.

## **Resultados principales**

A partir del análisis exploratorio se encontraron los siguientes resultados:

- Se identificó una relación positiva entre el tempo musical y la cadencia de los corredores. La correlación entre BPM promedio de la música y pasos por minuto (SPM) fue de aproximadamente 0.72, indicando una asociación positiva entre ambas variables.

- Los rangos de BPM más altos presentaron mayores valores promedio de cadencia. En particular, las canciones dentro de rangos superiores a 160 BPM estuvieron asociadas con valores más elevados de pasos por minuto en los corredores.

- El análisis del catálogo de Spotify mostró que existen suficientes canciones disponibles dentro de los rangos de BPM relacionados con mayores valores de cadencia, especialmente entre 160 y 179 BPM.

- Las visualizaciones permitieron observar la diferencia entre la distribución de canciones disponibles y los rangos de tempo asociados con una mayor cadencia durante la actividad de running.

## Limitaciones

Aunque los resultados muestran una relación entre el tempo musical y la cadencia, existen algunas limitaciones en el análisis:

- La correlación encontrada no implica que un mayor BPM sea la causa directa de una mayor cadencia.

- El dataset de corredores corresponde a condiciones experimentales específicas y puede no representar a todos los corredores.

- La cadencia puede verse afectada por otros factores como nivel de entrenamiento, velocidad, fatiga, terreno o preferencias personales.

- El análisis considera principalmente el BPM de la música, sin evaluar otros elementos musicales como género, intensidad o estructura rítmica.
## Conclusiones

El análisis realizado permitió identificar una relación positiva entre el tempo musical medido en BPM y la cadencia de los corredores medida en SPM. Los resultados sugieren que canciones con tempos más altos pueden estar asociadas con mayores valores de cadencia durante una sesión de running.

Sin embargo, los resultados deben interpretarse como una asociación y no como una relación causal, debido a que existen múltiples factores que pueden influir en la cadencia de un corredor.

Este proyecto demuestra cómo la integración de datos musicales y deportivos puede generar información útil para la selección de música durante entrenamientos. Como trabajo futuro, sería posible incorporar más variables como velocidad, género musical, intensidad del ejercicio o preferencias individuales para obtener un análisis más completo.
## SEGUNDA ENTREGA
## Descripción de la segunda entrega
En esta segunda etapa del proyecto desarrollamos un sistema de recomendación musical utilizando Python. Partiendo del análisis de la primera entrega, donde estudiamos la relación entre los BPM de las canciones y la cadencia de los corredores, buscamos aplicar esos resultados para crear una herramienta que pueda recomendar música de acuerdo con los gustos del usuario y el tipo de ejercicio que realizará.

El sistema permite que una persona ingrese tres de sus canciones favoritas y seleccione el tipo de entrenamiento que hará ese día. Con esta información, el programa analiza las características musicales de las canciones y busca otras similares dentro de nuestro catálogo.

El objetivo es generar una playlist personalizada que tenga un mínimo de 10 canciones y una duración de al menos 40 minutos, considerando tanto las preferencias musicales del usuario como el ritmo del ejercicio.
## Objetivo
Desarrollar un sistema de recomendación que utilice las características musicales de las canciones y técnicas de análisis de datos para generar playlists personalizadas para diferentes tipos de entrenamiento.

Buscamos que las recomendaciones no dependan únicamente de los BPM, sino también de qué tanto se parecen las canciones a las preferencias del usuario.

## Ampliación del dataset
Para esta segunda entrega decidimos ampliar nuestra base de datos de Spotify, ya que queríamos que el sistema tuviera más opciones al momento de recomendar canciones.

En la primera entrega trabajamos con un dataset de aproximadamente 114,000 registros de canciones. Para esta etapa incorporamos otro dataset obtenido de Kaggle, llamado Spotify 1.2M+ Songs, que contiene aproximadamente 1.2 millones de registros.
Este nuevo dataset incluye información como:

- Nombre de la canción y artista.
- BPM o tempo musical.
- Energía de la canción.
- Qué tan bailable es.
- Qué tan alegre o positiva es.
- Intensidad del sonido.
- Duración de la canción.
- Otras características musicales.
Antes de utilizar los datos, revisamos que las columnas fueran compatibles con nuestro código y realizamos una limpieza para eliminar canciones repetidas y registros con valores inválidos.

Con esto logramos ampliar considerablemente el catálogo disponible para generar recomendaciones.

## Metodología del sistema de recomendación
Para desarrollar el recomendador utilizamos Python y librerías como Pandas, NumPy, Scikit-learn y Matplotlib.

El funcionamiento del sistema se dividió en las siguientes etapas:
1. Selección de canciones favoritas:Primero, el programa solicita al usuario que ingrese tres canciones que le gusten.
Al escribir el nombre de una canción, el sistema busca coincidencias dentro del dataset y muestra las opciones disponibles, incluyendo el artista y los BPM. Esto permite seleccionar la versión correcta de cada canción.
Las tres canciones elegidas sirven como punto de partida para conocer las preferencias musicales del usuario.
2. Selección del tipo de ejercicio

Después, el usuario selecciona el entrenamiento que realizará. Incluimos cinco opciones:
- Caminata.
- Trote suave.
- Running moderado.
- Running intenso.
- Entrenamiento por intervalos.
Cada actividad tiene un rango de BPM de referencia. Esto permite que el sistema considere el ritmo del entrenamiento al buscar las canciones.

Los rangos funcionan como una guía para recomendar música, pero no significan que todos los corredores deban mantener una cadencia específica.
3. Normalización de los datos con StandardScaler

Las características musicales tienen diferentes escalas. Por ejemplo, los BPM pueden tener valores de 160, mientras que la energía se representa con valores entre 0 y 1.
Para evitar que las variables con números más grandes tengan mayor influencia solamente por su escala, utilizamos StandardScaler.
Esta herramienta transforma los datos para que las características se puedan comparar de una manera más equilibrada.

4. Reducción de dimensionalidad con PCA
Una de las partes principales de esta entrega fue aplicar PCA (Principal Component Analysis), también conocido como Análisis de Componentes Principales.

Esta técnica permite reducir la cantidad de variables que utilizamos para representar cada canción, conservando la mayor parte de la información estadística.
En nuestro caso, trabajamos con nueve características musicales y configuramos el PCA para conservar al menos el 90 % de la varianza de los datos.
Esto nos permite representar las canciones en un espacio de menos dimensiones y facilita el cálculo de similitudes entre ellas.
Es importante mencionar que conservar el 90 % de la varianza no significa que las recomendaciones tengan un 90 % de precisión, sino que se mantiene gran parte de la información utilizada para comparar las canciones.
5. Cálculo de similitud mediante distancia euclidiana
Una vez aplicado el PCA, el sistema utiliza las tres canciones favoritas del usuario para calcular un centroide.
El centroide representa el punto promedio de las tres canciones dentro del espacio generado por PCA.

Posteriormente, calculamos la distancia euclidiana entre ese punto y las canciones del catálogo. Las canciones con distancias más pequeñas se consideran más similares a las preferencias musicales del usuario.
Además, el sistema toma en cuenta el rango de BPM correspondiente al ejercicio seleccionado para realizar las recomendaciones.
6. Generación de la playlist
Finalmente, el programa selecciona las canciones recomendadas hasta cumplir las condiciones establecidas:
- Un mínimo de 10 canciones.
- Una duración total de al menos 40 minutos.
- Canciones relacionadas con las preferencias del usuario.
- BPM adecuados al rango de referencia del ejercicio.

El resultado se presenta en una tabla que incluye el nombre de cada canción, artista, BPM, duración, distancia calculada con PCA y enlace a Spotify.
También se genera un archivo CSV que permite guardar las recomendaciones.

## Visualización de resultados
Para entender mejor cómo funciona el recomendador, generamos una gráfica que representa las canciones utilizando los dos primeros componentes principales del PCA.

En esta gráfica utilizamos diferentes colores para identificar:

- Puntos azules: una muestra de las canciones del catálogo.
- Estrellas naranjas: las tres canciones favoritas del usuario.
- Puntos verdes: las canciones recomendadas.
- Cruz roja: el centroide calculado a partir de las tres canciones favoritas.

Esta visualización nos ayuda a observar cómo se distribuyen las canciones y qué tan cerca están las recomendaciones del punto que representa las preferencias del usuario.

Aunque la gráfica utiliza dos componentes para facilitar su interpretación, el cálculo de distancias considera el espacio PCA utilizado por el modelo.

## Resultados obtenidos
Para comprobar que nuestro sistema funcionaba correctamente, realizamos una prueba utilizando las siguientes canciones:


Artista: The Weeknd
Blinding Lights
Artista: Dua Lipa
Levitating
Artista:
Dont Start Now

El tipo de ejercicio seleccionado fue running intenso.
A partir de estas preferencias, el sistema generó una playlist con los siguientes resultados:
En la prueba realizada, seleccionamos el entrenamiento de running intenso y el sistema generó una playlist de 13 canciones con una duración total aproximada de 43 minutos y 23 segundos, cumpliendo con los requisitos mínimos de 10 canciones y 40 minutos. Las canciones recomendadas tuvieron un tempo de aproximadamente 160 a 162 BPM, adecuado al rango establecido para este tipo de entrenamiento. Para seleccionar las canciones, utilizamos PCA y distancia euclidiana, lo que permitió identificar aquellas con características musicales similares a las tres canciones favoritas del usuario.

Los resultados muestran que el sistema logró generar una playlist que cumple con los requisitos establecidos.

También observamos que las canciones recomendadas se encontraban relativamente agrupadas cerca del centroide dentro de la visualización, lo que nos permitió identificar cómo el modelo selecciona canciones de acuerdo con sus características musicales.

Sin embargo, notamos que varias recomendaciones tenían BPM muy similares y que algunas canciones eran poco conocidas. Esto nos permitió identificar oportunidades para mejorar el sistema y lograr un mayor equilibrio entre el ritmo del entrenamiento y los gustos del usuario.

## Limitaciones
Aunque logramos desarrollar un sistema funcional, identificamos algunas limitaciones:

- La similitud musical se calcula a partir de características numéricas, por lo que dos canciones pueden parecerse en sus datos, pero no necesariamente gustarle a la misma persona.
- El sistema utiliza rangos de BPM como referencia, pero la cadencia de una persona también depende de factores como su velocidad, condición física y experiencia.
- El nuevo dataset contiene canciones de diferentes años, pero no incluye todos los lanzamientos musicales recientes.
- El sistema genera las recomendaciones y sus enlaces a Spotify, pero no crea automáticamente una playlist dentro de una cuenta de Spotify.
- Actualmente, el recomendador no aprende de las canciones que el usuario acepta o rechaza.

## Conclusiones de la segunda entrega



