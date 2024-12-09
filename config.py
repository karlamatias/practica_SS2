import psycopg2
import json

# Configuracion de datos para acceder a la base de datos
host = 'localhost' 
database = 'covid_data'
user = 'postgres'
password = '12345'

# Cadena de conexión para PostgreSQL
connection_string = f"dbname={database} user={user} password={password} host={host}"

def db_connection():
    try:
        connection = psycopg2.connect(connection_string)
        return connection
    except Exception as e:
        print(f"Error de conexión: {str(e)}")
        return None
 
 #Funcion para ejecutar el ingreso a la base de datos, aqui se define el contador
 # commit_cont para los correctos
 # rollback_cont para los fallidos 
    
def execute_queries(db_conn, queries):
    commit_cont = 0
    rollback_cont = 0
    for q in queries:
        if execute_query(db_conn, q):
            commit_cont += 1
        else:
            rollback_cont += 1
    report = {
        'commit_cont': commit_cont,
        'rollback_cont': rollback_cont
    }
    return report


#Ejecutar las inserciones a la base de datos
def execute_query(db_conn, query):
    reintentos = 0
    max_reintentos = 3
    while reintentos <= max_reintentos:
        try:
            cursor = db_conn.cursor()
            cursor.execute(query)
            db_conn.commit()
            return True
        except Exception as e:
            print(f"Ocurrió un error al insertar: {str(e)}")
            db_conn.rollback()
            reintentos += 1
            if reintentos <= max_reintentos:
                print(f"Reintentando ({reintentos}/{max_reintentos})...")
            else:
                print(f"Se alcanzó el número máximo de reintentos.")
                return False
        finally:
            cursor.close()
