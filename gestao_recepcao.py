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

def registar_dono():
    try:
        conn = ligar()
        cursor = conn.cursor()

        nome = input("Nome: ").strip()
        if not nome:
            print("Erro: Nome obrigatório.")
            return

        nif = input("NIF: ")
        telefone = input("Telefone: ")
        email = input("Email: ")

        cursor.execute(
            "INSERT INTO donos (nome, nif, telefone, email) VALUES (%s, %s, %s, %s)",
            (nome, nif, telefone, email)
        )

        conn.commit()
        print("✔ Dono registado!")
    except:
        print("Erro ao registar dono.")
    finally:
        conn.close()

def listar_donos():
    conn = ligar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_dono, nome, telefone FROM donos WHERE ativo = 1")

    print("\n--- DONOS ATIVOS ---")
    for d in cursor.fetchall():
        print(f"ID:{d[0]} | Nome:{d[1]} | Tel:{d[2]}")

    conn.close()

def registar_animal():
    try:
        conn = ligar()
        cursor = conn.cursor()

        nome = input("Nome: ")
        especie = input("Espécie: ")
        raca = input("Raça: ")
        data = input("Data (YYYY-MM-DD): ")
        id_dono = input("ID dono: ")

        if not existe(cursor, "donos", "id_dono", id_dono):
            print("Erro: Dono não existe.")
            return

        cursor.execute("""
            INSERT INTO animais (nome, especie, raca, data_nascimento, id_dono)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, especie, raca, data, id_dono))

        conn.commit()
        print("✔ Animal registado!")
    except:
        print("Erro ao registar animal.")
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

    print("\n--- ANIMAIS ATIVOS ---")
    for a in cursor.fetchall():
        print(f"ID:{a[0]} | Animal:{a[1]} | Dono:{a[2]}")

    conn.close()

def arquivar_animal():
    try:
        conn = ligar()
        cursor = conn.cursor()

        id_animal = input("ID do animal a arquivar: ")

        if not existe(cursor, "animais", "id_animal", id_animal):
            print("Erro: Animal não existe.")
            return

        cursor.execute("UPDATE animais SET ativo = 0 WHERE id_animal = %s", (id_animal,))
        conn.commit()

        print("✔ Animal arquivado com sucesso!")
    except:
        print("Erro ao arquivar animal.")
    finally:
        conn.close()

def menu():
    while True:
        print("\n--- RECEÇÃO ---")
        print("1. Registar dono")
        print("2. Listar donos")
        print("3. Registar animal")
        print("4. Listar animais")
        print("5. Arquivar animal")
        print("0. Voltar")

        op = input("Escolha: ")

        if op == "1":
            registar_dono()
        elif op == "2":
            listar_donos()
        elif op == "3":
            registar_animal()
        elif op == "4":
            listar_animais()
        elif op == "5":
            arquivar_animal()
        elif op == "0":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()