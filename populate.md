# Populate

O comando `populate` popula o banco com dados de teste usando `Faker("pt_BR")`.

Uso completo:

```bash
.venv/bin/python manage.py populate
```

Uso limpando os dados antes:

```bash
.venv/bin/python manage.py populate --clear
```

## Dados gerados no populate completo

A população da base de dados foi realizada de forma controlada, utilizando os
seguintes volumes de registros e relações:

- 10 categorias;
- 10 tags;
- 100 produtos;
- 1 registro de estoque para cada produto;
- 1000 usuários;
- 3 endereços para cada usuário;
- 10 pedidos para cada usuário;
- 3 tags para cada produto;
- 5 itens para cada pedido;
- Cada item relacionado a um produto aleatório;
- Cada item com quantidade entre 1 e 4 unidades;
- 5 registros de status para cada pedido;
- 10 avaliações (reviews) para cada produto.

As relações entre os registros foram definidas da seguinte forma:

- Cada categoria pode possuir uma categoria pai, pois as 5 últimas categorias
  são associadas como subcategorias das 5 primeiras.
- Cada produto pertence a uma categoria.
- Cada produto é associado a 3 tags.
- Cada produto possui 1 registro de estoque, com quantidade entre 10 e 400.
- Cada endereço pertence a um usuário.
- Cada pedido pertence a um usuário.
- Cada pedido utiliza um endereço pertencente ao próprio usuário do pedido.
- Cada item de pedido pertence a um pedido.
- Cada item de pedido referencia um produto.
- Cada registro de status pertence a um pedido.
- Cada avaliação pertence a um produto.
- Cada avaliação é feita por um usuário aleatório.

## Detalhes por entidade

### Categorias

As categorias são fixas:

- Eletrônicos
- Livros
- Moda
- Beleza
- Esportes
- Casa
- Brinquedos
- Alimentos
- Saúde
- Automotivo

As 5 últimas categorias recebem como `parent` uma das 5 primeiras.

### Tags

As tags são fixas:

- Novo
- Mais vendido
- Promoção
- Premium
- Sustentável
- Popular
- Exclusivo
- Recomendado
- Clássico
- Edição limitada

### Produtos

Cada produto recebe:

- 1 categoria aleatória.
- Preço entre 25.00 e 1200.00.
- 3 tags aleatórias.

### Usuários

Cada usuário recebe:

- `username`
- `email`
- `first_name`
- `last_name`
- senha padrão `password123`

### Endereços

Cada usuário recebe 3 endereços, com:

- `street`
- `city`

### Pedidos

Cada usuário recebe 10 pedidos.

Cada pedido:

- pertence a 1 usuário.
- usa 1 endereço aleatório daquele usuário.
- possui 5 itens.

Importante: "5 itens por pedido" significa a quantidade de linhas `OrderItem`
dentro do pedido.

Cada `OrderItem`:

- aponta para 1 produto aleatório.
- tem `quantity` entre 1 e 4.

Ou seja: cada pedido sempre possui 5 linhas de item. Como cada item pode ter
até 4 unidades, um pedido pode ter até 20 unidades no total.

### Status dos pedidos

Cada pedido recebe os 5 status abaixo, sempre nesta sequência:

- Pendente
- Aprovado
- Em preparação
- Enviado
- Entregue

### Reviews

Cada produto fica com 10 reviews.

Cada review recebe:

- 1 produto.
- 1 usuário aleatório.
- `rating` entre 1 e 5.

## Flags disponíveis

O comando também permite popular apenas partes específicas:

```bash
.venv/bin/python manage.py populate --category
.venv/bin/python manage.py populate --tag
.venv/bin/python manage.py populate --product
.venv/bin/python manage.py populate --stock
.venv/bin/python manage.py populate --user
.venv/bin/python manage.py populate --address
.venv/bin/python manage.py populate --order
.venv/bin/python manage.py populate --review
```

Também é possível combinar com `--clear`:

```bash
.venv/bin/python manage.py populate --clear --order
```

## Observação

Algumas funções carregam registros já existentes com `objects.all()` depois de
criar novos dados. Por isso, se o comando for executado sem `--clear`, os novos
dados podem se misturar com dados antigos.
