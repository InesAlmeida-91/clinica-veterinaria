from db import ligar
from werkzeug.security import check_password_hash

def autenticar(username, password):
    """
    Devolve o utilizador se as credenciais estiverem corretas, ou None.
    """
    conn = ligar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM utilizadores
        WHERE username = %s AND ativo = 1
        """,
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return user

    return None