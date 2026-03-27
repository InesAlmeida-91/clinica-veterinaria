
from db import ligar, existe

def registar_dono(nome, nif, telefone, email):
    conn = ligar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO donos (nome, nif, telefone, email) VALUES (%s, %s, %s, %s)",
            (nome, nif, telefone, email)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Erro ao registar dono:", e)
        return False
    finally:
        conn.close()

def listar_donos():
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_dono, nome, telefone FROM donos WHERE ativo = 1")
    donos = cursor.fetchall()
    conn.close()
    return donos  # lista de tuples (id_dono, nome, telefone)

def registar_animal(nome, especie, raca, data_nascimento, id_dono):
    conn = ligar()
    cursor = conn.cursor()
    try:
        if not existe(cursor, "donos", "id_dono", id_dono):
            return False, "Dono não existe."
        cursor.execute("""
            INSERT INTO animais (nome, especie, raca, data_nascimento, id_dono)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, especie, raca, data_nascimento, id_dono))
        conn.commit()
        return True, None
    except Exception as e:
        print("Erro ao registar animal:", e)
        return False, "Erro ao registar animal."
    finally:
        conn.close()

def listar_animais():
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id_animal, a.nome, d.nome
        FROM animais a
        JOIN donos d ON a.id_dono = d.id_dono
        WHERE a.ativo = 1
    """)
    animais = cursor.fetchall()
    conn.close()
    return animais  # (id_animal, nome_animal, nome_dono)

def arquivar_animal(id_animal):
    conn = ligar()
    cursor = conn.cursor()
    try:
        if not existe(cursor, "animais", "id_animal", id_animal):
            return False, "Animal não existe."
        cursor.execute("UPDATE animais SET ativo = 0 WHERE id_animal = %s", (id_animal,))
        conn.commit()
        return True, None
    except Exception as e:
        print("Erro ao arquivar animal:", e)
        return False, "Erro ao arquivar animal."
    finally:
        conn.close()
