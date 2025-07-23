import pyodbc
import re
from sqlalchemy import text, insert
from datetime import datetime

# Configurações de conexão com o SQL Server
server = 'VALDEIR\SQLEXPRESS,1533'  # Nome do servidor SQL Server
database_autenticacao_compras = 'autenticacao_compras'  # Nome do banco de dados de autenticação
database_fiocruz = 'fiocruz'  # Nome do banco de dados Fiocruz
username = 'fiocruz'  # Nome de usuário
password = 'fiocruz'  # Senha

# Strings de conexão
connection_string_autenticacao_compras = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database_autenticacao_compras};'
    f'UID={username};'
    f'PWD={password};'
)

connection_string_fiocruz_compras = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database_fiocruz};'
    f'UID={username};'
    f'PWD={password};'
)

#############################################################################################################################################

def authenticate_user(nome_usuario, senha):
    try:
        conn = pyodbc.connect(connection_string_autenticacao_compras)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM cadastro WHERE login COLLATE Latin1_General_BIN = ? AND senha COLLATE Latin1_General_BIN = ?", 
            (nome_usuario, senha)
        )
        user = cursor.fetchone()
        conn.close()
        return user
    except pyodbc.Error as erro:
        print("Erro ao verificar os dados de login: ", erro)
        return None
    
#############################################################################################################################################

def add_user(nome, login, senha):
    try:
        conn = pyodbc.connect(connection_string_autenticacao_compras)
        cursor = conn.cursor()

        # Verifica se o login já existe
        query_check = "SELECT COUNT(*) FROM cadastro WHERE login = ?"
        cursor.execute(query_check, (login,))
        if cursor.fetchone()[0] > 0:
            print(f"Login '{login}' já existe.")
            return False

        # Insere o novo usuário
        query_insert = "INSERT INTO cadastro (nome, login, senha) VALUES (?, ?, ?)"
        cursor.execute(query_insert, (nome, login, senha))
        conn.commit()
        conn.close()
        print("Usuário inserido com sucesso.")
        return True
    except pyodbc.Error as e:
        print(f"Erro ao inserir os dados: {e}")
        return False
    
#############################################################################################################################################

def update_historico(matricula, **kwargs):
    try:
        with pyodbc.connect(connection_string_fiocruz_compras) as conn:
            with conn.cursor() as cursor:

                # 1. Buscar ID_Profissional baseado na matrícula
                query_id_profissional = "SELECT ID_Profissional FROM Dados_Pessoais WHERE Matricula = ?"
                cursor.execute(query_id_profissional, matricula)
                row_profissional = cursor.fetchone()
                if not row_profissional:
                    print(f"Erro: Nenhum profissional encontrado para a matrícula {matricula}")
                    return False
                id_profissional = row_profissional[0]

                # 2. Inserir nova linha em Historico_Profissionais
                query_insert = """
                    INSERT INTO Historico_Profissionais (
                        ID_Profissional, ID_Funcional, Escolaridade, Habilitacao, Nivel_Escolaridade, Titulacao,
                        Data_Inicio_Escolaridade, Data_Fim_Escolaridade, Plano, Carreira, Cargo,
                        Nivel_Cargo, Data_Inicio_Cargo, Data_Fim_Cargo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    id_profissional, kwargs['id_funcional'], kwargs['escolaridade'], kwargs['habilitacao'], kwargs['nivel_escolaridade'], kwargs['titulacao'],
                    kwargs['data_inicio_escolaridade'], kwargs['data_fim_escolaridade'], kwargs['plano'], kwargs['carreira'],
                    kwargs['cargo'], kwargs['nivel_cargo'], kwargs['data_inicio_cargo'], kwargs['data_fim_cargo']
                )
                cursor.execute(query_insert, params)
                conn.commit()

                print(f"Histórico salvo com sucesso para ID_Profissional: {id_profissional}")
                return True
            
    except pyodbc.Error as erro:
        print(f"Erro ao atualizar histórico: {erro}")
        return False