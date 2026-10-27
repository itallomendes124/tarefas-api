"""Testes da API. Usa apenas unittest da biblioteca padrao.

Rode com:  python -m unittest -v
"""
import os
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import json
from http.server import ThreadingHTTPServer

import db
import servidor


def requisitar(metodo, url, corpo=None):
    """Faz uma requisicao HTTP e devolve (status, json)."""
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(url, data=dados, method=metodo)
    if dados:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TesteAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # banco temporario, apagado no fim
        cls.fd, cls.caminho = tempfile.mkstemp(suffix=".db")
        cls.servidor = ThreadingHTTPServer(("127.0.0.1", 0), servidor.Handler)
        cls.servidor.caminho_db = cls.caminho
        cls.porta = cls.servidor.server_address[1]
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.porta}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        os.close(cls.fd)
        os.unlink(cls.caminho)

    def test_01_lista_comeca_vazia(self):
        status, corpo = requisitar("GET", f"{self.base}/tarefas")
        self.assertEqual(status, 200)
        self.assertEqual(corpo, [])

    def test_02_cria_tarefa(self):
        status, corpo = requisitar("POST", f"{self.base}/tarefas", {"titulo": "Estudar SQL"})
        self.assertEqual(status, 201)
        self.assertEqual(corpo["titulo"], "Estudar SQL")
        self.assertEqual(corpo["feita"], 0)
        self.assertIn("id", corpo)

    def test_03_cria_sem_titulo_falha(self):
        status, corpo = requisitar("POST", f"{self.base}/tarefas", {"titulo": "   "})
        self.assertEqual(status, 400)
        self.assertIn("erro", corpo)

    def test_04_busca_tarefa_existente(self):
        _, criada = requisitar("POST", f"{self.base}/tarefas", {"titulo": "Ler PDF"})
        status, corpo = requisitar("GET", f"{self.base}/tarefas/{criada['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(corpo["titulo"], "Ler PDF")

    def test_05_busca_inexistente_da_404(self):
        status, corpo = requisitar("GET", f"{self.base}/tarefas/99999")
        self.assertEqual(status, 404)
        self.assertIn("erro", corpo)

    def test_06_atualiza_marca_feita(self):
        _, criada = requisitar("POST", f"{self.base}/tarefas", {"titulo": "Treino"})
        status, corpo = requisitar("PUT", f"{self.base}/tarefas/{criada['id']}", {"feita": True})
        self.assertEqual(status, 200)
        self.assertEqual(corpo["feita"], 1)
        self.assertEqual(corpo["titulo"], "Treino")  # titulo nao muda

    def test_07_atualiza_titulo_vazio_falha(self):
        _, criada = requisitar("POST", f"{self.base}/tarefas", {"titulo": "X"})
        status, _ = requisitar("PUT", f"{self.base}/tarefas/{criada['id']}", {"titulo": ""})
        self.assertEqual(status, 400)

    def test_08_deleta_tarefa(self):
        _, criada = requisitar("POST", f"{self.base}/tarefas", {"titulo": "Apagar"})
        status, _ = requisitar("DELETE", f"{self.base}/tarefas/{criada['id']}")
        self.assertEqual(status, 200)
        status, _ = requisitar("GET", f"{self.base}/tarefas/{criada['id']}")
        self.assertEqual(status, 404)  # confirma que sumiu

    def test_09_deleta_inexistente_da_404(self):
        status, _ = requisitar("DELETE", f"{self.base}/tarefas/99999")
        self.assertEqual(status, 404)

    def test_10_rota_desconhecida_da_404(self):
        status, _ = requisitar("GET", f"{self.base}/qualquer")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
