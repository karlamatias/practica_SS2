# Practica Unica 

## Explicacion de la Practica

Esta practica consiste en la limpieza y analisis de datos, tiene como objetivo procesar informacion relacionada con fallecimientos a nivel mundial y por municipio de Guatemala. Se divide en las siguientes partes:

  - Modulo mundiales ('mundiales.py'): Este modulo descarga un archivo que esta alojado en la nube, en este caso Google Drive, procesa los datos de fallecimiento a nivel mundial. Realiza la limpieza de duplicados, eliminacion de registros no relevantes y estandarizacion de campos invalidos. La clase mundiales encapsula la logica y funciones realcionadas con los datos a nivel mundial

  - Modulo municipios ('municipios.py'): Procesa datos de fallecimientos por municipio, realiza limpieza de duplicados, eliminacion de registros no relevantes y estandarizacion de campos invalidos La clase municipios encapsula la logica y funciones relacionadas con los datos por municipio.

   - Modulo Principal ('main.py'): Es el modulo principal de la practica, este orquesta la limpieza y analisis de los datos tanto a nivel mundial como por municipio.

## Proceso de Limpieza de Datos

    1. Seleccion de año: Solicita al usuario el año que desea analizar, para poder filtrar los datos de ambos archivos.
   
    2. Seleccion de Archivos: Solicita al usuario la ruta del archivo de fallecimientos por municipio y el enlace del archivo de fallecimientos a nivel mundial, los cuales son cargados y procesados en un dataset de pandas.

    3. Limpieza de Dato Mundiales: Cada uno de los dataset es limpiado en funcioness personalizadas, ya que cada dataset cuenta con una estructura completamente diferente, dicha limpieza involucra varios filtros.

     4. Eliminacion de duplicados y registros no relevantes: Estandariza campos invalidos y  maneja los datos faltantes

     5. Validacion de fechas en formato correspondiente y validacion de campos numericos, para que no posean valores negativos o alfabeticos

     6. Transformacion del dataset de datos por municipio, de tal forma que sea compatible con la estructura del dataset de los casos a nivel mundial.

     7. Union de ambos dataset en base a la fecha y posteriormente ingreso a una base de datos (PostgreSQL) en bloques de 50 paquetes o inserciones hasta llegar al total de registros.

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

## Inicializacion del Proyecto

1. Ejecutar el Proyecto Principal

```bash
python main.py