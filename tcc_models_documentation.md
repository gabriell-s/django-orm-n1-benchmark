# 📦 Projeto TCC - Modelagem de Dados

Este documento descreve a modelagem de dados utilizada no projeto **tcc**, no aplicativo **core**.  
O objetivo dessa estrutura é permitir a simulação de cenários complexos de acesso a dados utilizando ORM, possibilitando a análise de performance e identificação de problemas como **N+1 queries**.

---

## 🧩 Visão Geral

A base foi construída simulando um sistema de e-commerce com múltiplos níveis de relacionamento:

- Relações simples (1:1, 1:N)
- Relações complexas (N:N)
- Relações reversas
- Encadeamento profundo de dados

---

## 👤 User

Representa o usuário do sistema.

```python
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
```

### Relacionamentos:
- 1:N com **Address**
- 1:N com **Order**
- 1:N com **Review**

---

## 🏠 Address

Endereços associados ao usuário.

```python
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
```

---

## 🗂️ Category

Categoria de produtos com suporte a hierarquia.

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )
```

### Relacionamentos:
- Auto-relacionamento (hierarquia)
- 1:N com **Product**

---

## 🏷️ Tag

Tags para classificação de produtos.

```python
class Tag(models.Model):
    name = models.CharField(max_length=50)
```

---

## 📦 Product

Produto disponível para compra.

```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tags = models.ManyToManyField(Tag, related_name="products")
```

### Relacionamentos:
- N:1 com **Category**
- N:N com **Tag**
- 1:1 com **Stock**
- 1:N com **Review**

---

## 📊 Stock

Controle de estoque do produto.

```python
class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stock")
    quantity = models.IntegerField()
```

---

## ⭐ Review

Avaliação de produtos feita por usuários.

```python
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
```

### Relacionamentos:
- N:1 com **Product**
- N:1 com **User**

---

## 🛒 Order

Pedido realizado por um usuário.

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 📄 OrderItem

Itens que compõem um pedido.

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
```

---

## 🔄 OrderStatusHistory

Histórico de status do pedido.

```python
class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# 🔗 Fluxo de Relacionamentos Complexos

Exemplo de navegação profunda:

User
 ├── addresses
 ├── orders
 │    ├── items
 │    │    ├── product
 │    │    │    ├── category → parent
 │    │    │    ├── tags
 │    │    │    └── reviews → user
 │    └── status_history

---

# 🎯 Objetivo da Modelagem

Essa modelagem foi projetada para:

- Simular cenários reais de sistemas web
- Gerar consultas complexas com múltiplos relacionamentos
- Demonstrar problemas de performance (N+1 queries)
- Permitir testes com:
  - `select_related`
  - `prefetch_related`

---

# ⚠️ Pontos de Atenção

- Relações profundas podem gerar alto número de consultas
- Relações N:N exigem uso de `prefetch_related`
- Hierarquias aumentam complexidade de acesso

---

# 🚀 Uso no TCC

Essa base será utilizada para:

- Comparar consultas com e sem otimização
- Medir número de queries executadas
- Avaliar impacto no tempo de resposta
