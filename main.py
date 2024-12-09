import os

import pandas as pd
from colorama import init, Fore

from itertools import batched
from config import db_connection, execute_queries, execute_query
from municipios import Municipios
from mundiales import Mundiales
from query import insert_total_muertes_municipio

init()
os.system("cls")


def pause():
    print('Presiona una tecla para continuar...')
    input()

def transformation(data_municipio, data_mundial):
    # Obtener las fechas 
    fechas = data_municipio.columns[5:]

    # Convertir el DataFrame de formato ancho a largo usando melt
    data_municipio_trans = pd.melt(data_municipio, id_vars=['departamento', 'codigo_departamento', 'municipio', 'codigo_municipio', 'poblacion'], value_vars=fechas, var_name='fecha', value_name='casos')

    # Convertir la columna 'fecha' al formato correcto
    data_municipio_trans['fecha'] = pd.to_datetime(data_municipio_trans['fecha'], format='%m/%d/%Y', errors='coerce')
    data_municipio_trans = data_municipio_trans.dropna(subset=['fecha'])

    # Ordenar el DataFrame
    data_municipio_trans = data_municipio_trans.sort_values(by=['departamento', 'municipio', 'fecha'])

    # Restablecer el índice
    data_municipio_trans = data_municipio_trans.reset_index(drop=True)

    # Convertir la columna 'Date_reported' de el archivo de datos mundiales al formato de fecha
    data_mundial['Date_reported'] = pd.to_datetime(data_mundial['Date_reported'], format='%Y-%m-%d')

    # Renombrar columnas 
    data_mundial = data_mundial.rename(columns={'New_cases': 'new_cases_world', 'Cumulative_cases': 'cumulative_cases_world', 'New_deaths': 'new_deaths_world', 'Cumulative_deaths': 'cumulative_deaths_world'})

    # Combinar los DataFrames basándonos en la columna 'Date_reported' y 'fecha'
    data_combinada = pd.merge(data_municipio_trans, data_mundial, left_on='fecha', right_on='Date_reported', how='left')

    # Eliminar la columna 'Date_reported'
    data_combinada = data_combinada.drop('Date_reported', axis=1)

    # Convertir las columnas a valores enteros
    # Rellenar NaN con 0 antes de la conversión
    data_combinada['cumulative_cases_world'] = data_combinada['cumulative_cases_world'].fillna(0).astype(int)
    data_combinada['cumulative_deaths_world'] = data_combinada['cumulative_deaths_world'].fillna(0).astype(int)

    data_combinada['fecha'] = pd.to_datetime(data_combinada['fecha'])
    data_combinada = data_combinada.dropna()

    data_combinada.to_csv('dataCompinada.csv', index=False)

    return data_combinada

#INSERSION A LA DATA BASE
#Insertar el pais
def insert_pais(data_mundial):
    pais = data_mundial[['Country_code', 'Country']]
    pais = pais.drop_duplicates()

    try:
        conn = db_connection()
        for index, row in pais.iterrows():
            codigo_pais = row['Country_code']
            nombre_pais = row['Country']

            query = f"INSERT INTO pais (codigo_pais, nombre_pais) VALUES ('{codigo_pais}', '{nombre_pais}')"
            execute_query(conn, query)
            print("Se realizó con éxito la inserción de paises")
    except Exception as e:
        print(f"Ocurrió un error al ejecutar la conexión")
    finally:
        conn.close()
    
#Insertar departamentos    
def insert_departamentos(data_departamento):
    departmento = data_departamento[['codigo_departamento','departamento']]
    departmento = departmento.drop_duplicates()


    try:
        conn = db_connection()
        for index, row in departmento.iterrows():
            codigo_departamento = row['codigo_departamento']
            nombre_departamento = row['departamento']

            query = f"INSERT INTO departamento (codigo_departamento, nombre_departamento) VALUES ('{codigo_departamento}', '{nombre_departamento}')"
            execute_query(conn, query)
    except Exception as e:
        print(f"Ocurrió un error al ejecutar la inserción del departamento")
    finally:
        conn.close()

#Insertar municipios
def insert_municipios(data_municipios):
    selected_columns = ['codigo_departamento', 'codigo_municipio', 'municipio', 'poblacion']
    municipios = data_municipios[selected_columns]
    municipios = municipios.drop_duplicates(subset=['codigo_municipio', 'municipio'])

    try: 
        conn = db_connection()
        for index, row in municipios.iterrows():
            codigo_municipio = row['codigo_municipio']
            nombre_municipio = row['municipio']
            id_departamento = row['codigo_departamento']
            poblacion = row['poblacion']

            query = f"INSERT INTO municipio (codigo_municipio, nombre_municipio, poblacion, id_departamento) VALUES ('{codigo_municipio}', '{nombre_municipio}', '{poblacion}', '{id_departamento}')"
            execute_query(conn, query)

    except Exception as e:
        print("Ocurrió un error al ejecutar la inserción de un municipio")
    finally:
        conn.close()

#Insertar muertes por pais
def insert_casos_pais(data_mundial):
    selected_columns = ['Date_reported', 'New_cases','Cumulative_cases','New_deaths','Cumulative_deaths']
    info_mundial = data_mundial[selected_columns]
    info_mundial =  info_mundial.drop_duplicates(subset=['Date_reported'])

    try:
        conn = db_connection()
        for index, row in info_mundial.iterrows():
            fecha = row['Date_reported']
            cod_pais = 'GT'
            new_cases = row['New_cases']
            cumulative_cases = row['Cumulative_cases']
            new_deaths = row['New_deaths']
            cumulative_deaths = row['Cumulative_deaths']

            query = f"INSERT INTO casos_mundiales (cod_pais, fecha, new_cases, cumulative_cases, new_death, cumulative_death) VALUES ('{cod_pais}', '{fecha}', {new_cases}, {cumulative_cases}, {new_deaths}, {cumulative_deaths})"
            execute_query(conn, query)

    except Exception as e:
        print("Ocurrió un error al insertar la información de country deaths")
    finally:
        conn.close()


def insert_departments_municipalities(data_municipio):
    insert_departamentos(data_municipio)
    insert_municipios(data_municipio)

def insert_data(data_municipio, data_mundial, final_data):
    insert_pais(data_mundial)
    insert_casos_pais(data_mundial)
    insert_departments_municipalities(data_municipio)
    insert_final_data(final_data)

def insert_final_data(final_data):
    new_order_columns = ['codigo_municipio', 'fecha', 'casos', 'new_cases_world']
    data = final_data[new_order_columns]
    
    queries = make_md_batches(list(data.itertuples()))  # Asegúrate de que se genera una cadena
    
    insert_to_database(queries)  # Pasar la cadena, no la lista


def insert_to_database(queries):
    conn = db_connection()
    print(f"{Fore.YELLOW}Reporte de Inserción de Bloques{Fore.RESET}")
    for i, query in enumerate(queries, 1):  # Enumerar los bloques
        try:
            # Ejecutar cada query
            report = execute_queries(conn, [query])
            print(f"{Fore.LIGHTGREEN_EX}Bloque {i}: Exitoso{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}Bloque {i}: Fallido - {e}{Fore.RESET}")

        # Mostrar reporte después de cada bloque
        print(f"{Fore.CYAN}Procesados hasta el Bloque {i}{Fore.RESET}")
        print(f"  {Fore.LIGHTGREEN_EX}Exitosos: {report['commit_cont']}{Fore.RESET}")
        print(f"  {Fore.RED}Fallidos: {report['rollback_cont']}{Fore.RESET}")

        # Pausar después de cada bloque
        if i % 50 == 0 or i == len(queries):  # Pausa cada 50 o al final
            pause()

    conn.close()

def make_md_batch(registers):
    query_values = ""
    
    for i, row in enumerate(registers):
        codigo_municipio, fecha, casos, new_cases_world = row.codigo_municipio, row.fecha, row.casos, row.new_cases_world
        fecha_str = fecha.strftime('%Y-%m-%d')
        query_values += "({}, '{}', {}, {}),\n".format(codigo_municipio, fecha_str, casos, new_cases_world)
    return query_values[:-2] + ";\n"

def make_md_batches(registers, batch_size=50):
    batches = divide_batches(registers, batch_size)
    queries = []
    for batch in batches:
        query = insert_total_muertes_municipio + make_md_batch(batch)
        queries.append(query)
    
    return queries

def divide_batches(list_parameter, n):
    return list(batched(list_parameter, n))


municipios = Municipios()
mundiales = Mundiales()

# Leer data de municipios
by_year_municipio = municipios.get_year_from_user()
by_municipio_csv = municipios.get_municipality_file_path()
data_municipio = pd.read_csv(by_municipio_csv)
os.system("cls")

print(f"{Fore.LIGHTGREEN_EX}El archivo {by_municipio_csv} fue seleccionado con éxito{Fore.RESET}")

# Data Mundial 
data_mundial = mundiales.get_world_file()
if data_mundial is not None:
    print(f"{Fore.LIGHTGREEN_EX}La data se ha leído con éxito{Fore.RESET}")
    pause()
    os.system("cls")

    print(f"{Fore.YELLOW}Limpiando Data de Municipios{Fore.RESET}")
    data_municipio = municipios.clear_municipality_data(data_municipio)
    print('Data por municipio')
    print(data_municipio)
    pause()

    print(f"{Fore.YELLOW}Limpiando Data de Municipios{Fore.RESET}")
    data_mundial = mundiales.clear_world_data(data_mundial)
    print('Data Mundial')
    print(data_mundial)
    pause()

    print(f"{Fore.YELLOW}Transformando Data{Fore.RESET}")
    final_data = transformation(data_municipio, data_mundial)
    print(f"{Fore.LIGHTGREEN_EX}La data se ha transformado con éxito{Fore.RESET}")
    print(final_data)

    insert_data(data_municipio, data_mundial, final_data)

    pause()