# Practica Unica 

## Explicacion de la Practica

Esta practica consiste en la limpieza y analisis de datos, tiene como objetivo procesar informacion relacionada con fallecimientos a nivel mundial y por municipio de Guatemala. Se divide en las siguientes partes:

  - Modulo mundiales ('mundiales.py'): Este modulo descarga un archivo que esta alojado en la nube, en este caso Google Drive, procesa los datos de fallecimiento a nivel mundial. Realiza la limpieza de duplicados, eliminacion de registros no relevantes y estandarizacion de campos invalidos. La clase mundiales encapsula la logica y funciones realcionadas con los datos a nivel mundial

  - Modulo municipios ('municipios.py'): Procesa datos de fallecimientos por municipio, realiza limpieza de duplicados, eliminacion de registros no relevantes y estandarizacion de campos invalidos La clase municipios encapsula la logica y funciones relacionadas con los datos por municipio.

   - Modulo Principal ('main.py'): Es el modulo principal de la practica, este orquesta la limpieza y analisis de los datos tanto a nivel mundial como por municipio.

## Proceso de Limpieza de Datos

    - Seleccion de año: Solicita al usuario el año que desea analizar, para poder filtrar los datos de ambos archivos.
   
    - Seleccion de Archivos: Solicita al usuario la ruta del archivo de fallecimientos por municipio y el enlace del archivo de fallecimientos a nivel mundial, los cuales son cargados y procesados en un dataset de pandas.

    - Limpieza de Dato Mundiales: Cada uno de los dataset es limpiado en funcioness personalizadas, ya que cada dataset cuenta con una estructura completamente diferente, dicha limpieza involucra varios filtros.

    - Eliminacion de duplicados y registros no relevantes: Estandariza campos invalidos y  maneja los datos faltantes

    - Validacion de fechas en formato correspondiente y validacion de campos numericos, para que no posean valores negativos o alfabeticos

    - Transformacion del dataset de datos por municipio, de tal forma que sea compatible con la estructura del dataset de los casos a nivel mundial.

    - Union de ambos dataset en base a la fecha y posteriormente ingreso a una base de datos (PostgreSQL) en bloques de 50 paquetes o inserciones hasta llegar al total de registros.

# Explicacion del Modelo de Datos

## Modelo de datos: covid_data

### Tabla: PAIS

 - codigo_pais (PK, varchar(5)) - Codigo del pais 
 - nombre_pais (varchar(50))- Nombre del pais

### Tabla: CASOS_MUNDIALES 
 
 - id_pais (PK, FK a pais.codigo_pais, varchar(5)) - Codigo del pais
 - fecha (PK, datetime) - Fecha
 - new_cases (int) - Nuevos Casos
 - cumulative_cases (int) - Casos Acumulados
 - new_death (int) - Nuevas Muertes
 - cumulative_death (int) - Muertes Acumuladas

### Tabla: DEPARTAMENTO

 - codigo_departamento (PK, int) - Codigo del departamento 
 - nombre_departemento (varchar(50)) - Nombre del departamento

### Tabla: MUNICIPIO

 - codigo_municipio (PK, int) - Codigo del municipio
 - nombre_municipio (varchar(50)) -  Nombre del municipio
 - poblacion (int) - Poblacion del municipio
 - id_departamento (FK, DEPARTAMENTO.codigo_departamento, (int)) - Codigo del departamento

### Tabla: FALLECIDOS_MUNICIPIO

 - id_municipio (PK, FK MUNICIPIO.codigo_municipio, int) - Codigo del municipio
 - fecha (FK, datetime) - Fecha
 - fallecidos (int) - Total de muertes en el municipio
 - casos_mundiales (int) - Muertes del dia en el pais

# Proyecto Fase 2

*Nota: Para esta fase del proyecto, no se realizo ninguna modificacion en la logica anterior, la base de datos se utilizo como se creo desde la practica. Todos los calculos que se realizaron se realizaron con formulas propias de Power BI y utilizando las tablas y columnas que se tenian en la base de datos llamada covid_data*

## Dashboard "Fallecidos por Municipio"

- Formula: Tasa Mortalidad = 
DIVIDE(
    SUM('public fallecidos_municipio'[fallecidos]),
    SUMX(RELATEDTABLE('public municipio'), 'public municipio'[poblacion]),
    0
) * 100000
 
Esta fórmula calcula la tasa de mortalidad ajustada por cada 100,000 personas en un municipio. El proceso es el siguiente:
 - Se suman los fallecidos en todos los municipios.
 - Se suman las poblaciones de esos municipios relacionados.
 - Se calcula la tasa de mortalidad dividiendo el número de fallecidos entre la población total y luego se multiplica por 100,000 para obtener una tasa estandarizada.


- Formula: MaxFallecimientosPorDia = 
MAX('public fallecidos_municipio'[fallecidos])

- DIAS_REGISTRADO = DISTINCTCOUNT('public fallecidos_municipio'[fecha])

- Analisis de Correlacion -> coeficiente de correlación de Pearson entre dos variables: la población de los municipios y el número de muertes en esos mismos municipios

Formula: Correlacion_Poblacion_Muertes = 
VAR Promedio_X = AVERAGE('public municipio'[poblacion])
VAR Promedio_Y = AVERAGE('public fallecidos_municipio'[fallecidos])
VAR Numerador = 
    SUMX(
        'public municipio',
        ('public municipio'[poblacion] - Promedio_X) * 
        (LOOKUPVALUE('public fallecidos_municipio'[fallecidos], 'public fallecidos_municipio'[ID_municipio], 'public municipio'[codigo_municipio]) - Promedio_Y)
    )
VAR Denominador_X = 
    SUMX(
        ALL('public municipio'),
        ('public municipio'[poblacion] - Promedio_X) ^ 2
    )
VAR Denominador_Y = 
    SUMX(
        ALL('public fallecidos_municipio'),
        ('public fallecidos_municipio'[fallecidos] - Promedio_Y) ^ 2
    )
VAR Denominador = SQRT(Denominador_X * Denominador_Y)
RETURN
    IF(Denominador <> 0, Numerador / Denominador, 0)

### Explicacion Formula:
- Primero se calcula el promedio de cada una de las variables, los fallecidos y las muertes
- El numerador de la fórmula de correlación es la covarianza entre las dos variables.
- El denominador se calcula en dos partes: la suma de los cuadrados de las desviaciones de la población (X) y de las muertes (Y).
- Finalmente, se calcula el denominador como el producto de las desviaciones estándar de las dos variables (población y muertes), es decir, el producto de las raíces cuadradas de las varianzas
- Finalmente, se realiza la división entre el numerador (covarianza) y el denominador (producto de las desviaciones estándar).
Si el denominador es diferente de 0, se calcula la correlación de Pearson. Si el denominador es 0 (lo que ocurriría si las desviaciones estándar son 0, es decir, si todas las poblaciones o muertes son iguales), se devuelve 0 como resultado, evitando así una división por 0.


## Gráfica de Muertes por Municipio (Circular):

- Motivo: Las gráficas circulares son ideales para mostrar proporciones relativas en un conjunto de datos. En este caso, permiten observar visualmente cómo se distribuyen las muertes totales entre los municipios, destacando fácilmente cuáles tienen mayor o menor impacto.
- Ventajas: El uso de colores y números hace que sea más comprensible y atractivo para los usuarios, destacando rápidamente los municipios más afectados.

## Gráfico de Relación entre Población y Muertes (Tabla):

- Motivo: Una tabla es adecuada para datos comparativos detallados. Permite al usuario observar directamente los valores exactos de población y muertes para cada municipio, facilitando un análisis más preciso.
- Ventajas: La claridad y precisión de los datos ayudan a realizar comparaciones directas sin necesidad de interpretar gráficos.

## Visualización de Tasa de Mortalidad (Gráfica de Cintas):

- Motivo: Las gráficas de cintas destacan bien la magnitud de valores específicos para cada categoría (en este caso, municipios). Permiten una comparación clara entre las tasas de mortalidad.
- Ventajas: La representación visual de las tasas en cintas de diferentes longitudes hace que sea intuitivo identificar rápidamente los municipios con mayores o menores tasas.

## Gráfico de Muertes Acumuladas (Líneas):

- Motivo: Las gráficas de líneas son ideales para mostrar tendencias a lo largo del tiempo. En este caso, permiten visualizar cómo evolucionaron las muertes acumuladas día a día, mes a mes o año a año.
- Ventajas: Ayudan a identificar patrones y picos en el tiempo, facilitando un análisis temporal.
Dashboard "Fallecidos por Departamento":

## Gráfico de Muertes Registradas (Tabla):

- Motivo: Una tabla permite comparar de manera directa los valores de población y muertes totales por departamento. Es útil para un análisis detallado y exacto.
- Ventajas: La claridad de los datos en formato tabular facilita el acceso rápido a información específica.

## Gráfico de Muertes Totales por Departamento (Anillos):

- Motivo: Los gráficos de anillos son visualmente atractivos y similares a las gráficas circulares. Resaltan proporciones entre departamentos y facilitan la comprensión de qué porcentaje del total de muertes corresponde a cada uno.
- Ventajas: Ofrecen una representación intuitiva con colores y porcentajes claros.

## Evolución Diaria de Muertes entre Departamentos (Cintas):

- Motivo: Las gráficas de cintas permiten visualizar cómo evolucionaron las muertes diarias, destacando las diferencias entre departamentos. Cada cinta representa un departamento, lo que facilita la comparación.
- Ventajas: Los colores y la forma continua de las cintas muestran tendencias y permiten identificar fácilmente patrones de aumento o disminución.

## Gráfica de Tasa de Mortalidad por Departamento (Barras Apiladas):

- Motivo: Las barras apiladas son ideales para comparar tasas de mortalidad entre departamentos. Cada barra representa un departamento, y la longitud de la barra refleja la magnitud de la tasa.
- Ventajas: Facilita la comparación directa entre departamentos y destaca visualmente las diferencias.

## Gráfica de Muertes Acumuladas por Fecha (Líneas):

- Motivo: Las gráficas de líneas son excelentes para mostrar cómo han evolucionado las muertes acumuladas a lo largo del tiempo. Cada punto en la línea representa un valor acumulado en una fecha específica.
- Ventajas: Claridad en la representación de tendencias temporales y la identificación de fechas clave con mayores incrementos.


## Gráfico de Muertes por Día y Muertes Acumuladas (Columnas Apiladas y Líneas):
- Motivo: Se utiliza para comparar las muertes diarias con las acumuladas, mostrando cómo las muertes diarias contribuyen al total acumulado con una visualización temporal clara.

- Ventajas: Las columnas apiladas permiten ver la contribución de cada categoría (por municipio, fecha, etc.) al total de muertes por día.
Las líneas facilitan la visualización de las tendencias y la evolución de las muertes acumuladas a lo largo del tiempo.

## Gráfico de Muertes Acumuladas y Muertes Acumuladas Globales (Circular):
- Motivo: Se utiliza para mostrar la comparación entre las muertes acumuladas en Guatemala y las muertes acumuladas a nivel global. Un gráfico circular es ideal para representar proporciones relativas de un total.

- Ventajas: El gráfico circular facilita la comparación visual de las partes de un total, mostrando qué porcentaje de las muertes globales corresponden a Guatemala.

## Gráfico de Muertes Globales por Día (Medidos):
- Motivo: El medidor es útil para visualizar un valor único, como el total de muertes globales por día, comparado con un objetivo o rango deseado.

- Ventajas: Medidores proporcionan una manera clara y rápida de ver un valor clave, como las muertes diarias, y compararlo con un umbral o referencia para una interpretación sencilla y destacada.

## Gráfico de Tasa de Mortalidad de Guatemala y Global (Dispersión):
- Motivo: Se utiliza para comparar la tasa de mortalidad de Guatemala y la global, permitiendo observar la relación entre ambas variables y si existen correlaciones o patrones similares.

- Ventajas: El gráfico de dispersión es ideal para mostrar cómo varían dos variables continuas y permite detectar patrones o correlaciones entre las tasas de mortalidad de Guatemala y global.

### Razones Generales para la Selección de las Gráficas:

## Gráficas Circulares y de Anillos: 
Destacan proporciones relativas y son visualmente atractivas para resúmenes generales.

## Tablas: 
Útiles para mostrar detalles exactos cuando se necesita precisión numérica.

## Gráficas de Cintas y Barras Apiladas: 
Ideales para comparar categorías y resaltar valores relativos.

## Gráficas de Líneas: 
Perfectas para análisis temporal, mostrando tendencias y evoluciones.
Este enfoque asegura que cada tipo de gráfica sea utilizado de manera que maximice la comprensión y facilite el análisis de los datos relevantes.

