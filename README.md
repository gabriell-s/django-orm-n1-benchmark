# django-orm-n1-benchmark

Análise de performance de ORM (N+1 queries) com Django REST Framework, desenvolvida como parte de um TCC.

API de um e-commerce simulado, construída com **Django** e **Django REST Framework**, usada para
medir o impacto do problema de **N+1 queries** e comparar estratégias de otimização do ORM
(`select_related` e `prefetch_related`) em endpoints com relacionamentos profundos.

## Stack

- Python 3.14
- Django 6 + Django REST Framework
- PostgreSQL 15 (via Docker) ou SQLite (desenvolvimento local)
- Faker (geração de dados), Pandas, django-debug-toolbar
- [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências

## Estrutura

```
.
├── shop/
│   ├── settings.py, urls.py        # Configuração do projeto Django
│   ├── pagination/                 # Classes de paginação (page_size via query param)
│   └── core/
│       ├── models/                 # User, Address, Category, Tag, Product, Stock,
│       │                           # Order, OrderItem, OrderStatusHistory, Review
│       ├── serializers/            # Serializers aninhados (users, orders, products)
│       ├── views/                  # ViewSets somente leitura
│       ├── related/                # Definição de select/prefetch por endpoint
│       ├── router.py               # Rotas da API
│       └── management/commands/
│           ├── populate.py         # Popula o banco com dados falsos
│           └── benchmark_api.py    # Executa o benchmark dos endpoints
├── benchmark_api/                  # Resultados (CSVs) e script de sumarização
├── docker-compose.yaml             # Postgres (com latência de rede simulada) + web
├── populate.md                     # Detalhes dos dados gerados pelo populate
├── tree.md                         # Estrutura de retorno de cada endpoint
├── tcc_models_documentation.md     # Documentação da modelagem de dados
└── modelo.png                      # Diagrama do modelo de dados
```

## Como rodar

### Com Docker (recomendado)

```bash
docker compose up --build
```

Sobe o PostgreSQL (com **10 ms de latência de rede** simulada via `tc netem`, para evidenciar o
custo de cada query) e a aplicação em `http://localhost:8000`. As migrations são aplicadas
automaticamente.

Para popular o banco dentro do container:

```bash
docker compose exec web python3 manage.py populate
```

### Localmente

```bash
cp .env.example .env      # ajuste DATABASE_URL se necessário
uv sync
uv run python manage.py migrate
uv run python manage.py populate
uv run python manage.py runserver
```

## Endpoints

Todos são somente leitura e paginados (`?page=` e `?page_size=`, máximo 10000).

| Endpoint          | Descrição                                                        |
| ----------------- | ---------------------------------------------------------------- |
| `/api/users/`     | Usuários com endereços, pedidos, itens, produtos, categoria e tags |
| `/api/orders/`    | Pedidos com usuário, endereço, itens e histórico de status        |
| `/api/products/`  | Produtos com categoria, tags, estoque e avaliações                |

A estrutura completa de cada resposta está em [tree.md](tree.md).

### Estratégias de carregamento

Cada endpoint aceita query params que ativam as otimizações do ORM:

| Parâmetro              | Efeito                                                       |
| ---------------------- | ------------------------------------------------------------ |
| _(nenhum)_             | Sem otimização — evidencia o N+1                             |
| `?select=true`         | Aplica `select_related` (JOINs para relações FK/1:1)         |
| `?prefetch=true`       | Aplica `prefetch_related` (queries separadas para relações N) |
| `?select=true&prefetch=true` | Combina as duas estratégias                            |
| `?prefetch_select=true`| Usa `prefetch_related` também para as relações de `select`   |

Exemplo:

```bash
curl "http://localhost:8000/api/users/?page_size=100&prefetch=true"
```

## Populando o banco

```bash
python manage.py populate            # popula tudo
python manage.py populate --clear    # apaga os dados antes de popular
python manage.py populate --product  # popula apenas uma entidade
```

Volumes padrão: 1000 usuários, 100 produtos, 10 pedidos por usuário, 5 itens por pedido, entre
outros. Veja [populate.md](populate.md) para o detalhamento completo.

## Benchmark

O comando `benchmark_api` chama cada endpoint com todas as estratégias e diferentes tamanhos de
página, medindo o **tempo de resposta** e a **quantidade de queries** executadas. O
debug-toolbar é desativado durante a medição.

```bash
python manage.py benchmark_api                       # 10 execuções, todos os endpoints
python manage.py benchmark_api --runs 5 --api users  # apenas /api/users/
python manage.py benchmark_api --append              # continua um benchmark interrompido
```

Cada execução gera um arquivo `benchmark_api/api_benchmark_XX.csv` com as colunas
`endpoint, strategy, page_size, time_ms, query_count, status_code, response_bytes, error`.

Para gerar as tabelas com as médias por endpoint:

```bash
python benchmark_api/summarize_benchmarks.py
```

O script lê os CSVs de `benchmark_api/resultados_tcc/` e salva o resultado em
`benchmark_api/benchmark_api_<endpoint>.txt`. Para resumir uma execução nova, gere-a com
`--output-dir benchmark_api/resultados_tcc` (isso substitui os CSVs usados no TCC).

### Resultados utilizados no TCC

Os CSVs das 10 execuções analisadas no trabalho estão em
[`benchmark_api/resultados_tcc/`](benchmark_api/resultados_tcc/). Executar o benchmark novamente gera
novos arquivos: a contagem de queries se repete, mas os tempos variam, pois os dados são gerados
sem semente fixa.

## Documentação

- [Modelagem de dados](tcc_models_documentation.md) e [diagrama](modelo.png)
- [Dados gerados pelo populate](populate.md)
- [Estrutura de retorno dos endpoints](tree.md)
