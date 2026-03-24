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

def marcar_consulta():
    try:
        conn = ligar()
        cursor = conn.cursor()

        data = input("Data (YYYY-MM-DD HH:MM:SS): ")
        motivo = input("Motivo: ")
        id_animal = input("ID animal: ")
        id_vet = input("ID veterinário: ")

        cursor.execute("SELECT ativo FROM animais WHERE id_animal = %s", (id_animal,))
        result = cursor.fetchone()

        if not result:
            print("Erro: Animal não existe.")
            return

        if result[0] == 0:
            print("Erro: Animal arquivado (ex: falecido).")
            return

        if not existe(cursor, "veterinarios", "id_vet", id_vet):
            print("Erro: Veterinário não existe.")
            return

        cursor.execute("""
            INSERT INTO consultas (data_consulta, motivo, id_animal, id_vet)
            VALUES (%s, %s, %s, %s)
        """, (data, motivo, id_animal, id_vet))

        conn.commit()
        print("✔ Consulta marcada!")
    except:
        print("Erro ao marcar consulta.")
    finally:
        conn.close()

def listar_consultas():
    conn = ligar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id_consulta, c.data_consulta, a.nome, v.nome
        FROM consultas c
        JOIN animais a ON c.id_animal = a.id_animal
        JOIN veterinarios v ON c.id_vet = v.id_vet
    """)

    print("\n--- CONSULTAS ---")
    for c in cursor.fetchall():
        print(f"ID:{c[0]} | Data:{c[1]} | Animal:{c[2]} | Vet:{c[3]}")

    conn.close()

def historico():
    conn = ligar()
    cursor = conn.cursor()

    id_animal = input("ID do animal: ")

    cursor.execute("""
        SELECT id_consulta, data_consulta, motivo
        FROM consultas
        WHERE id_animal = %s
    """, (id_animal,))

    consultas = cursor.fetchall()

    print("\n--- HISTÓRICO CLÍNICO ---")
    for c in consultas:
        print(f"\nConsulta {c[0]} | {c[1]} | {c[2]}")

        cursor.execute("""
            SELECT t.nome, ct.quantidade, (ct.quantidade * t.preco)
            FROM consulta_tratamento ct
            JOIN tratamentos t ON ct.id_tratamento = t.id_tratamento
            WHERE ct.id_consulta = %s
        """, (c[0],))

        for t in cursor.fetchall():
            print(f"  Tratamento: {t[0]} | Total: {t[2]}€")

    conn.close()

def relatorio_gastos():
    conn = ligar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.nome, SUM(ct.quantidade * t.preco)
        FROM donos d
        JOIN animais a ON d.id_dono = a.id_dono
        JOIN consultas c ON a.id_animal = c.id_animal
        JOIN consulta_tratamento ct ON c.id_consulta = ct.id_consulta
        JOIN tratamentos t ON ct.id_tratamento = t.id_tratamento
        GROUP BY d.nome
    """)

    print("\n--- GASTOS POR DONO ---")
    for r in cursor.fetchall():
        print(f"{r[0]} -> {r[1]}€")

    conn.close()

def menu():
    while True:
        print("\n--- CONSULTAS ---")
        print("1. Marcar consulta")
        print("2. Listar consultas")
        print("3. Histórico clínico")
        print("4. Relatório de gastos")
        print("0. Voltar")

        op = input("Escolha: ")

        if op == "1":
            marcar_consulta()
        elif op == "2":
            listar_consultas()
        elif op == "3":
            historico()
        elif op == "4":
            relatorio_gastos()
        elif op == "0":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()