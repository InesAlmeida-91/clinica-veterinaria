# services_consultas.py
from db import ligar, existe

def marcar_consulta(data_consulta, motivo, id_animal, id_vet):
    conn = ligar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ativo FROM animais WHERE id_animal = %s", (id_animal,))
        result = cursor.fetchone()
        if not result:
            return False, "Animal não existe."
        if result[0] == 0:
            return False, "Animal arquivado (ex: falecido)."

        if not existe(cursor, "veterinarios", "id_vet", id_vet):
            return False, "Veterinário não existe."

        cursor.execute("""
            INSERT INTO consultas (data_consulta, motivo, id_animal, id_vet)
            VALUES (%s, %s, %s, %s)
        """, (data_consulta, motivo, id_animal, id_vet))
        conn.commit()
        return True, None
    except Exception as e:
        print("Erro ao marcar consulta:", e)
        return False, "Erro ao marcar consulta."
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
    consultas = cursor.fetchall()
    conn.close()
    return consultas  # (id_consulta, data, nome_animal, nome_vet)

def historico_por_animal(id_animal):
    conn = ligar()
    cursor = conn.cursor()
    # consultas do animal
    cursor.execute("""
        SELECT id_consulta, data_consulta, motivo
        FROM consultas
        WHERE id_animal = %s
        ORDER BY data_consulta DESC
    """, (id_animal,))
    consultas = cursor.fetchall()

    historico = []
    for c in consultas:
        id_consulta = c[0]
        cursor.execute("""
            SELECT t.nome, ct.quantidade, (ct.quantidade * t.preco)
            FROM consulta_tratamento ct
            JOIN tratamentos t ON ct.id_tratamento = t.id_tratamento
            WHERE ct.id_consulta = %s
        """, (id_consulta,))
        tratamentos = cursor.fetchall()  # (nome_trat, quantidade, total)
        historico.append({
            "id_consulta": c[0],
            "data_consulta": c[1],
            "motivo": c[2],
            "tratamentos": tratamentos
        })

    conn.close()
    return historico

def relatorio_gastos_por_dono():
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
    relatorio = cursor.fetchall()  # (nome_dono, total)
    conn.close()
    return relatorio

def listar_tratamentos():
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_tratamento, nome, preco FROM tratamentos")
    tratamentos = cursor.fetchall()
    conn.close()
    return tratamentos  # (id_tratamento, nome, preco)

def adicionar_tratamento_a_consulta(id_consulta, id_tratamento, quantidade):
    conn = ligar()
    cursor = conn.cursor()
    try:
        if not existe(cursor, "consultas", "id_consulta", id_consulta):
            return False, "Consulta não existe."
        if not existe(cursor, "tratamentos", "id_tratamento", id_tratamento):
            return False, "Tratamento não existe."

        cursor.execute("""
            INSERT INTO consulta_tratamento (id_consulta, id_tratamento, quantidade)
            VALUES (%s, %s, %s)
        """, (id_consulta, id_tratamento, quantidade))
        conn.commit()
        return True, None
    except Exception as e:
        print("Erro ao associar tratamento:", e)
        return False, "Erro ao associar tratamento."
    finally:
        conn.close()
