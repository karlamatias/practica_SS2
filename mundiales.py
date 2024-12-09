import os
import pandas as pd
import chardet
from colorama import init, Fore
from io import StringIO
import requests
import re
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

#Comprobar si un valor es positivo y entero (Si algun registro contiene un valor negativo o no numerico, se elimina del DataFrame)
def is_positive_integer(value):
    try:
        return pd.notna(value) and int(value) >= 0
    except ValueError:
        return False
    
def is_valid_alpha(value):
    # Verifica si el valor contiene únicamente letras y espacios
    return all(char.isalpha() or char.isspace() for char in value)    

#Filtrar un DataFrame para incluir solo filas donde las columnas departamento y municipio contienen valores alfabéticos válidos.
def validate_alpha_columns(dataframe):
    # Aplica la función de validación a las columnas "departamento" y "municipio"
    condition = dataframe[['Country']].applymap(is_valid_alpha).all(axis=1)

    # Filtra el DataFrame original
    dataframe = dataframe[condition]

    return dataframe

#Eliminar columnas irrelevantes para nuestro analisis, en este caso, WHO_region
def remove_useless_columns(dataframe):
    useless_columns = ['WHO_region']
    dataframe = dataframe.drop(useless_columns, axis=1)
    return dataframe

# Función para agregar ceros a los meses y días de un solo dígito
def standardize_date_format(date_str):
    # Añadir ceros al mes y al día si es necesario
    return re.sub(r'(^|\D)(\d{1})(/\d{2}/|\d{4})', r'\01\2\3', date_str)

def standarize_data(dataframe):
    # Estandarizar fechas
    dataframe['Date_reported'] = dataframe['Date_reported'].apply(standardize_date_format)

    # Convertir las fechas a datetime, y manejar errores con 'coerce' para valores inválidos
    dataframe['Date_reported'] = pd.to_datetime(dataframe['Date_reported'], format='%m/%d/%Y', errors='coerce')

    # Eliminar filas donde 'Date_reported' es NaT
    dataframe = dataframe.dropna(subset=['Date_reported'])

    # Filtrar por año, si 'year' no es None
    if year is not None:
        dataframe = dataframe[dataframe['Date_reported'].dt.year == year]

    # Estandarizar datos numéricos
    numeric_columns = ['New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']
    dataframe.loc[:, numeric_columns] = dataframe[numeric_columns].fillna(0).replace('N/A', 0)

    # Filtrar filas donde al menos una columna numérica no es un entero positivo
    condition = dataframe[numeric_columns].apply(lambda x: x.map(is_positive_integer)).all(axis=1)
    dataframe = dataframe[condition]

    return dataframe




class Mundiales:

# Solicitar el año a analizar
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

    def get_world_file(self):
        while True:
            url = input("Enlace del Archivo de Fallecidos a Nivel Mundial (csv): ")

            # Verificar si la URL es de Google Drive
            if "drive.google.com" in url:
                # Usamos una expresión regular para extraer el FILE_ID de la URL
                match = re.search(r"\/d\/(.*?)\/", url)
                if match:
                    file_id = match.group(1)
                    # Crear el enlace de descarga directa
                    url = f"https://drive.google.com/uc?id={file_id}&export=download"
                else:
                    print(f"{Fore.RED}No se pudo extraer el FILE_ID de la URL. Verifique el formato del enlace.{Fore.RESET}")
                    continue

            # Hacer la solicitud HTTP para obtener el archivo
            response = requests.get(url)

            if response.status_code == 200:
                result = chardet.detect(response.content)
                encoding = result['encoding']
                
                text = response.content.decode(encoding)
                data = StringIO(text)

                # Leer el archivo CSV
                dataframe = pd.read_csv(data)

                return dataframe
            else:
                print(f"{Fore.RED}Hubo un error al descargar el archivo de la url {url}\nRevise que el enlace sea el correcto\nStatus: {response.status_code}{Fore.RESET}")

    def clear_world_data(self, dataframe):
        # Eliminar registros duplicados
        print(f"{Fore.CYAN}Eliminando Registros Duplicados{Fore.RESET}")
        dataframe = dataframe.drop_duplicates()

        # Filtrar las filas donde el código de país y eliminar columnas irrelevantes
        print(f"{Fore.CYAN}Eliminando datos irrelevantes para el análisis{Fore.RESET}")
        dataframe = dataframe[dataframe['Country_code'] == 'GT']
        dataframe = remove_useless_columns(dataframe)

        # Estandarizar datos
        print(f"{Fore.CYAN}Estandariazando Campos Inválidos{Fore.RESET}")
        dataframe.replace('N/A', pd.NA, inplace=True)
        # Estandarizar fecha
        dataframe = standarize_data(dataframe)


        print(f"{Fore.CYAN}Manejando Datos Faltantes{Fore.RESET}")

        print(f"{Fore.GREEN}Limpieza de Datos Mundiales Realizada con Éxito (Se Obtuvo solamente datos de Guatemala){Fore.RESET}")
        return dataframe
    