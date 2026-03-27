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
        SELECT c.id_consulta, c.data_consulta, a.nome, c.motivo, v.nome
        FROM consultas c
        JOIN animais a ON c.id_animal = a.id_animal
        JOIN veterinarios v ON c.id_vet = v.id_vet
        ORDER BY c.data_consulta DESC
    """)
    consultas = cursor.fetchall()
    conn.close()
    return consultas  # (id_consulta, data, nome_animal, motivo, nome_vet)

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

def listar_veterinarios():
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_vet, nome FROM veterinarios")
    veterinarios = cursor.fetchall()
    conn.close()
    return veterinarios  # (id_vet, nome)


def consulta_por_id(id_consulta):
    conn = ligar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT c.id_consulta, c.data_consulta, c.motivo, c.descricao, c.id_animal, c.id_vet, a.nome, v.nome FROM consultas c JOIN animais a ON c.id_animal = a.id_animal JOIN veterinarios v ON c.id_vet = v.id_vet WHERE c.id_consulta = %s", (id_consulta,))
        raw = cursor.fetchone()
        conn.close()
        if not raw:
            return None
        return {
            'id_consulta': raw[0],
            'data_consulta': raw[1],
            'motivo': raw[2],
            'descricao': raw[3],
            'id_animal': raw[4],
            'id_vet': raw[5],
            'nome_animal': raw[6],
            'nome_vet': raw[7],
        }
    except Exception:
        cursor.execute("SELECT c.id_consulta, c.data_consulta, c.motivo, c.id_animal, c.id_vet, a.nome, v.nome FROM consultas c JOIN animais a ON c.id_animal = a.id_animal JOIN veterinarios v ON c.id_vet = v.id_vet WHERE c.id_consulta = %s", (id_consulta,))
        raw = cursor.fetchone()
        conn.close()
        if not raw:
            return None
        return {
            'id_consulta': raw[0],
            'data_consulta': raw[1],
            'motivo': raw[2],
            'descricao': None,
            'id_animal': raw[3],
            'id_vet': raw[4],
            'nome_animal': raw[5],
            'nome_vet': raw[6],
        }


def atualizar_descricao_consulta(id_consulta, descricao):
    conn = ligar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM consultas WHERE id_consulta = %s", (id_consulta,))
        if not cursor.fetchone():
            return False, "Consulta não encontrada."

        # certificar que a coluna existe
        try:
            cursor.execute("UPDATE consultas SET descricao = %s WHERE id_consulta = %s", (descricao, id_consulta))
        except Exception:
            return False, "A coluna descricao não existe. Atualize a estrutura da BD"

        conn.commit()
        return True, None
    except Exception as e:
        print("Erro ao atualizar descrição:", e)
        return False, "Erro ao atualizar descrição"
    finally:
        conn.close()


def relatorio_gastos_filtro(id_dono=None, id_animal=None):
    conn = ligar()
    cursor = conn.cursor()
    query = """
        SELECT d.nome, a.nome, SUM(ct.quantidade * t.preco)
        FROM donos d
        JOIN animais a ON d.id_dono = a.id_dono
        JOIN consultas c ON a.id_animal = c.id_animal
        JOIN consulta_tratamento ct ON c.id_consulta = ct.id_consulta
        JOIN tratamentos t ON ct.id_tratamento = t.id_tratamento
    """
    params = []
    conditions = []
    if id_dono:
        conditions.append("d.id_dono = %s")
        params.append(id_dono)
    if id_animal:
        conditions.append("a.id_animal = %s")
        params.append(id_animal)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " GROUP BY d.nome, a.nome"
    cursor.execute(query, tuple(params))
    relatorio = cursor.fetchall()
    conn.close()
    return relatorio


def listar_tratamentos():
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_tratamento, nome, preco FROM tratamentos")
    tratamentos = cursor.fetchall()
    conn.close()
    return tratamentos  # (id_tratamento, nome, preco)

def tratamentos_por_consulta(id_consulta):
    conn = ligar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.nome, ct.quantidade, (ct.quantidade * t.preco), t.id_tratamento
        FROM consulta_tratamento ct
        JOIN tratamentos t ON ct.id_tratamento = t.id_tratamento
        WHERE ct.id_consulta = %s
    """, (id_consulta,))
    resultado = cursor.fetchall()
    conn.close()
    return resultado  # (nome, quantidade, total, id_tratamento)


def remover_tratamento_consulta(id_consulta, id_tratamento):
    conn = ligar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM consulta_tratamento WHERE id_consulta = %s AND id_tratamento = %s",
            (id_consulta, id_tratamento)
        )
        conn.commit()
        return True, None
    except Exception as e:
        print("Erro ao remover tratamento:", e)
        return False, "Erro ao remover tratamento."
    finally:
        conn.close()


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
