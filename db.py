import mysql.connector

def ligar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="clinica_veterinaria"
    )

def existe(cursor, tabela, campo, valor):
    cursor.execute(f"SELECT 1 FROM {tabela} WHERE {campo} = %s LIMIT 1", (valor,))
    return cursor.fetchone() is not None
