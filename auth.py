# auth.py
from db import ligar

def autenticar(username, password):
    """
    Devolve dict com utilizador se ok, ou None.
    Pressupõe tabela:
    CREATE TABLE utilizadores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(255),
        role VARCHAR(20),
        ativo TINYINT DEFAULT 1
    );
    """
    conn = ligar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM utilizadores WHERE username = %s AND password = %s AND ativo = 1",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user
