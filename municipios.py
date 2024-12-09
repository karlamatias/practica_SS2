import os
import pandas as pd
from colorama import init, Fore
from io import StringIO
import requests
init()

#year = 2020
year = None

#Solicitar el año a analizar
def get_year_from_user(self):
        while True:
            year_input = input(f"{Fore.YELLOW}Por favor ingresa el año que des analizar: {Fore.RESET}")
            if year_input.isdigit() and int(year_input) > 0:
                return int(year_input)  # Devuelve el año como un entero
            else:
                print(f"{Fore.RED}El año ingresado no es válido. Inténtalo de nuevo.{Fore.RESET}")

#Verificar si un valor es un entero positivo
def is_positive_integer(value):
    try:
        #Verificar si no es nulo 
        return pd.notna(value) and int(value) >= 0
    except ValueError:
        return False
    
def is_valid_alpha(value):
    # Verifica si el valor contiene únicamente letras y espacios
    return all(char.isalpha() or char.isspace() for char in value)

#Filtrar un DataFrame para incluir solo filas donde las columnas departamento y municipio contienen valores alfabéticos válidos.
def validate_alpha_columns(dataframe):
    # Aplica la función de validación a las columnas "departamento" y "municipio"
    condition = dataframe['departamento'].map(is_valid_alpha) & dataframe['municipio'].map(is_valid_alpha)

    # Filtra el DataFrame original
    dataframe = dataframe[condition]

    return dataframe

#Comprueba si una cadena tiene un formato de fecha válido (MM/DD/YYYY).
def is_valid_date_format(value):
    try:
        pd.to_datetime(value, format='%m/%d/%Y')
        return True
    except ValueError:
        return False


def standarize_data(dataframe):
    # filtrar columnas con fecha valida
    valid_date_columns = [col for col in dataframe.columns[5:] if is_valid_date_format(col)]

    # Obtener data del 2020
    dataframe = dataframe.drop(columns=[col for col in valid_date_columns if pd.to_datetime(col, format='%m/%d/%Y').year != year])

    # Validar que la data sean numeros
    # Rellena valores faltantes con 0 y reemplaza N/A por 0.
    # Filtra filas donde todas las columnas numéricas tengan valores positivos.
    numeric_columns = dataframe.columns[4:]
    dataframe[numeric_columns] = dataframe[numeric_columns].fillna(0).replace('N/A', 0)
    condition = dataframe[numeric_columns].apply(lambda col: col.map(is_positive_integer)).all(axis=1)

    dataframe = dataframe[condition]

    # Filtrar valores inválidos en columnas de texto.
    dataframe = validate_alpha_columns(dataframe)


    return dataframe


class Municipios:

    def __init__(self):
        pass  

    # Solicitar el año a analizar
    def get_year_from_user(self):
        global year  # Usar la variable global 'year'
        while True:
            year_input = input(f"{Fore.YELLOW}Por favor ingresa el año que deseas analizar: {Fore.RESET}")
            if year_input.isdigit() and int(year_input) > 0:
                year = int(year_input)  # Modificar la variable global
                return year
            else:
                print(f"{Fore.RED}El año ingresado no es válido. Inténtalo de nuevo.{Fore.RESET}")


    #Cargar el archivo de municipios, el csv esta en local, se valida que sea un archivo csv y que exista en el sistema de archivos
    def get_municipality_file_path(self):
        while True:
            file_path = input(f"{Fore.YELLOW}Ruta del Archivo de Fallecidos por Municipio (csv): {Fore.RESET}")

            if not file_path.lower().endswith('.csv'):
                print(f"{Fore.RED}El archivo debe tener extensión .csv, intentalo de nuevo{Fore.RESET}")
                continue

            if os.path.isfile(file_path):
                return file_path
            else:
                print(f"{Fore.RED}El archivo no existe (o no es válido), intentalo de nuevo{Fore.RESET}")

#Limpiamos la data
    def clear_municipality_data(self, dataframe):
        # Elimina registros duplicados
        print(f"{Fore.CYAN}Eliminando Registros Duplicados{Fore.RESET}")
        dataframe = dataframe.drop_duplicates()
        dataframe = dataframe.drop_duplicates(subset='codigo_municipio', keep='first')

        print(f"{Fore.CYAN}Eliminando datos irrelevantes para el análisis{Fore.RESET}")

        print(f"{Fore.CYAN}Estandarizando Campos Inválidos{Fore.RESET}")
        dataframe = standarize_data(dataframe)

        print(f"{Fore.CYAN}Manejando Datos Faltantes{Fore.RESET}")
        print(f"{Fore.GREEN}Limpieza de Datos por Municipio Realizada con Éxito{Fore.RESET}")
        return dataframe