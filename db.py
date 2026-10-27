"""Camada de banco de dados. Usa apenas sqlite3 da biblioteca padrao."""
import sqlite3

CAMINHO_PADRAO = "tarefas.db"


def conectar(caminho=CAMINHO_PADRAO):
    """Abre uma conexao e garante que a tabela existe."""
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo    TEXT    NOT NULL,
            feita     INTEGER NOT NULL DEFAULT 0,
            criada_em TEXT    NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    con.commit()
    return con


def criar(con, titulo):
    cur = con.execute("INSERT INTO tarefas (titulo) VALUES (?)", (titulo,))
    con.commit()
    return buscar(con, cur.lastrowid)


def listar(con):
    linhas = con.execute("SELECT * FROM tarefas ORDER BY id").fetchall()
    return [dict(l) for l in linhas]


def buscar(con, id_tarefa):
    linha = con.execute("SELECT * FROM tarefas WHERE id = ?", (id_tarefa,)).fetchone()
    return dict(linha) if linha else None


def atualizar(con, id_tarefa, titulo=None, feita=None):
    atual = buscar(con, id_tarefa)
    if atual is None:
        return None
    novo_titulo = titulo if titulo is not None else atual["titulo"]
    nova_feita = int(feita) if feita is not None else atual["feita"]
    con.execute(
        "UPDATE tarefas SET titulo = ?, feita = ? WHERE id = ?",
        (novo_titulo, nova_feita, id_tarefa),
    )
    con.commit()
    return buscar(con, id_tarefa)


def deletar(con, id_tarefa):
    cur = con.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
    con.commit()
    return cur.rowcount > 0  # True se apagou algo
