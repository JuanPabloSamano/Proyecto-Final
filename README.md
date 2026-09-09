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
