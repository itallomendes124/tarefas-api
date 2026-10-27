"""API REST de tarefas. Usa apenas http.server e json da biblioteca padrao.

Rotas:
    GET    /tarefas         lista todas
    POST   /tarefas         cria uma ({"titulo": "..."})
    GET    /tarefas/<id>    mostra uma
    PUT    /tarefas/<id>    atualiza ({"titulo": "...", "feita": true})
    DELETE /tarefas/<id>    apaga uma
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import db


class Handler(BaseHTTPRequestHandler):
    def responder(self, codigo, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def ler_json(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        if tamanho == 0:
            return {}
        bruto = self.rfile.read(tamanho)
        return json.loads(bruto.decode("utf-8"))

    def id_da_rota(self):
        """Extrai o numero de /tarefas/<id>. Retorna None se nao for valido."""
        partes = self.path.strip("/").split("/")
        if len(partes) == 2 and partes[0] == "tarefas" and partes[1].isdigit():
            return int(partes[1])
        return None

    def do_GET(self):
        con = db.conectar(self.server.caminho_db)
        if self.path.strip("/") == "tarefas":
            self.responder(200, db.listar(con))
        elif (tid := self.id_da_rota()) is not None:
            tarefa = db.buscar(con, tid)
            if tarefa:
                self.responder(200, tarefa)
            else:
                self.responder(404, {"erro": "tarefa nao encontrada"})
        else:
            self.responder(404, {"erro": "rota nao encontrada"})
        con.close()

    def do_POST(self):
        con = db.conectar(self.server.caminho_db)
        if self.path.strip("/") != "tarefas":
            self.responder(404, {"erro": "rota nao encontrada"})
            con.close()
            return
        try:
            dados = self.ler_json()
        except json.JSONDecodeError:
            self.responder(400, {"erro": "json invalido"})
            con.close()
            return
        titulo = (dados.get("titulo") or "").strip()
        if not titulo:
            self.responder(400, {"erro": "titulo e obrigatorio"})
        else:
            self.responder(201, db.criar(con, titulo))
        con.close()

    def do_PUT(self):
        con = db.conectar(self.server.caminho_db)
        tid = self.id_da_rota()
        if tid is None:
            self.responder(404, {"erro": "rota nao encontrada"})
            con.close()
            return
        try:
            dados = self.ler_json()
        except json.JSONDecodeError:
            self.responder(400, {"erro": "json invalido"})
            con.close()
            return
        titulo = dados.get("titulo")
        if titulo is not None:
            titulo = titulo.strip()
            if not titulo:
                self.responder(400, {"erro": "titulo nao pode ser vazio"})
                con.close()
                return
        atualizada = db.atualizar(con, tid, titulo=titulo, feita=dados.get("feita"))
        if atualizada:
            self.responder(200, atualizada)
        else:
            self.responder(404, {"erro": "tarefa nao encontrada"})
        con.close()

    def do_DELETE(self):
        con = db.conectar(self.server.caminho_db)
        tid = self.id_da_rota()
        if tid is None:
            self.responder(404, {"erro": "rota nao encontrada"})
        elif db.deletar(con, tid):
            self.responder(200, {"ok": True})
        else:
            self.responder(404, {"erro": "tarefa nao encontrada"})
        con.close()

    def log_message(self, *args):
        pass  # silencia o log padrao no terminal


def iniciar(porta=8000, caminho_db=db.CAMINHO_PADRAO):
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
    servidor.caminho_db = caminho_db
    print(f"API de tarefas em http://127.0.0.1:{porta}")
    print("Ctrl+C para parar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        servidor.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="API de tarefas")
    parser.add_argument("--porta", type=int, default=8000)
    parser.add_argument("--db", default=db.CAMINHO_PADRAO)
    args = parser.parse_args()
    iniciar(porta=args.porta, caminho_db=args.db)
