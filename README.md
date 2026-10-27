# Tarefas API

API REST de tarefas (lista de afazeres), escrita em **Python usando apenas a biblioteca padrão** — sem Flask, sem Django, sem `pip install`. Roda em qualquer lugar com Python 3.8+, incluindo Termux no Android.

> Projeto de estudo, criado para praticar backend: rotas HTTP, banco de dados e testes automatizados.

## O que faz

Guarda tarefas num banco SQLite e expõe uma API HTTP com as cinco operações básicas (CRUD):

| Método | Rota             | O que faz                                   |
|--------|------------------|---------------------------------------------|
| GET    | `/tarefas`       | lista todas as tarefas                      |
| POST   | `/tarefas`       | cria uma tarefa — corpo `{"titulo": "..."}` |
| GET    | `/tarefas/<id>`  | mostra uma tarefa                           |
| PUT    | `/tarefas/<id>`  | atualiza — `{"titulo": "...", "feita": true}` |
| DELETE | `/tarefas/<id>`  | apaga uma tarefa                            |

Validações: título obrigatório, título não pode ser vazio, id inexistente devolve 404, JSON inválido devolve 400.

## Como rodar

```
python servidor.py
```

Abre em `http://127.0.0.1:8000`. Para mudar a porta:

```
python servidor.py --porta 8123
```

## Exemplos (curl)

```
# criar
curl -X POST http://127.0.0.1:8000/tarefas -d '{"titulo":"Estudar backend"}'

# listar
curl http://127.0.0.1:8000/tarefas

# marcar como feita
curl -X PUT http://127.0.0.1:8000/tarefas/1 -d '{"feita":true}'

# apagar
curl -X DELETE http://127.0.0.1:8000/tarefas/1
```

## Testes

Dez testes automatizados, também só com a biblioteca padrão (`unittest`). Eles sobem o servidor numa porta livre, usam um banco temporário e conferem cada rota:

```
python -m unittest -v
```

## Estrutura

```
tarefas-api/
├── db.py          camada de banco de dados (sqlite3): criar, listar, buscar, atualizar, deletar
├── servidor.py    servidor HTTP e rotas (http.server)
├── test_api.py    testes automatizados (unittest)
└── README.md
```

## Como funciona

- `db.py` abre a conexão SQLite e cria a tabela `tarefas` na primeira execução. Toda query usa parâmetros `?`, para evitar SQL injection.
- `servidor.py` lê o método e o caminho da requisição, decide a rota e chama a função certa de `db.py`. As respostas são JSON.
- `test_api.py` sobe o servidor de verdade e faz requisições HTTP reais, verificando o código de status e o corpo de cada resposta.

## Limites

- Sem autenticação — feito para rodar localmente, como estudo.
- Banco em arquivo único (`tarefas.db`), sem migrações.
- Não cobre paginação nem filtros.

## Licença

MIT. Veja o arquivo `LICENSE`.
