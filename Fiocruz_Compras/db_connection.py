import pyodbc
from typing import Optional

# Configuração da conexão
SERVER = 'VALDEIR\\SQLEXPRESS,1533'
DATABASE = 'fiocruz_compras'
USERNAME = 'fiocruz'
PASSWORD = 'fiocruz'

# Função para criar a conexão com PyODBC
def get_pyodbc_connection(log=True) -> Optional[pyodbc.Connection]:
    try:
        conn = pyodbc.connect(
            f"DRIVER=ODBC Driver 17 for SQL Server;"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USERNAME};"
            f"PWD={PASSWORD};"
        )
        if log:
            print("Conexão PyODBC estabelecida com sucesso.")
        return conn
    except pyodbc.Error as e:
        print(f"Erro ao conectar com PyODBC: {e}")
        return None