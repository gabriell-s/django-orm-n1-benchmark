# Tree de retorno por view

## `/api/users/`
```
GET /api/users/ -> Lista de usuários
└─ user (object)
   ├─ id (integer)
   ├─ username (string)
   ├─ email (string)
   ├─ first_name (string)
   ├─ last_name (string)
   ├─ addresses (array)
   │  └─ address (object)
   │     ├─ id (integer)
   │     ├─ street (string)
   │     └─ city (string)
   └─ orders (array)
      └─ order (object)
         ├─ id (integer)
         ├─ address (object)
         │  ├─ id (integer)
         │  ├─ street (string)
         │  └─ city (string)
         ├─ created_at (datetime)
         └─ items (array)
            └─ order_item (object)
               ├─ id (integer)
               ├─ quantity (integer)
               └─ product (object)
                  ├─ id (integer)
                  ├─ name (string)
                  ├─ price (decimal)
                  ├─ category (object)
                  │  ├─ id (integer)
                  │  └─ name (string)
                  └─ tags (array)
                     └─ tag (object)
                        ├─ id (integer)
                        └─ name (string)
```

---

## `/api/orders/`
```
GET /api/orders/ -> Lista de pedidos
└─ order (object)
   ├─ id (integer)
   ├─ created_at (datetime)
   ├─ address (object)
   │  ├─ id (integer)
   │  ├─ street (string)
   │  └─ city (string)
   ├─ items (array)
   │  └─ order_item (object)
   │     ├─ id (integer)
   │     ├─ quantity (integer)
   │     └─ product (object)
   │        ├─ id (integer)
   │        ├─ name (string)
   │        ├─ price (decimal)
   │        ├─ category (object)
   │        │  ├─ id (integer)
   │        │  └─ name (string)
   │        └─ tags (array)
   │           └─ tag (object)
   │              ├─ id (integer)
   │              └─ name (string)
   └─ status_history (array)
      └─ status (object)
         ├─ id (integer)
         ├─ status (string)
         └─ created_at (datetime)
```

---

## `/api/products/`
```
GET /api/products/ -> Lista de produtos
└─ product (object)
   ├─ id (integer)
   ├─ name (string)
   ├─ price (decimal)
   ├─ category (object)
   │  ├─ id (integer)
   │  └─ name (string)
   ├─ tags (array)
   │  └─ tag (object)
   │     ├─ id (integer)
   │     └─ name (string)
   ├─ stock (object)
   │  ├─ id (integer)
   │  └─ quantity (integer)
   └─ reviews (array)
      └─ review (object)
         ├─ id (integer)
         ├─ user (string)
         └─ rating (integer)
```

---

## Query Params

Todos os endpoints suportam query params para variar a estratégia de relações:

- `select=true`: aplica `select_related` usando a lista `select` do endpoint.
- `prefetch=true`: aplica `prefetch_related` usando a lista `prefetch` do endpoint.
- `select=true&prefetch=true`: aplica as duas estratégias ao mesmo tempo.
- `prefetch_select=true`: aplica `prefetch_related` usando as listas `prefetch` e `select` do endpoint.

Esses parâmetros otimizam o queryset, mas retornam a mesma estrutura JSON.

## Paginação

Padrão: `SmallPagination` (10 items por página)
- Pode ser customizado por endpoint
- Query param: `page_size=50` para alternar entre tamanhos
