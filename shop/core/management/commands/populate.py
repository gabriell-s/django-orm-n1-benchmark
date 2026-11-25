from __future__ import annotations

import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count
from faker import Faker

from shop.core.models import (
    Address,
    Category,
    Order,
    OrderItem,
    OrderStatusHistory,
    Product,
    Review,
    Stock,
    Tag,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com dados de teste usando Faker."
    populate_options = (
        "category",
        "tag",
        "product",
        "stock",
        "user",
        "address",
        "order",
        "review",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Apaga os dados existentes antes de popular.",
        )
        for option in self.populate_options:
            parser.add_argument(
                f"--{option}",
                action="store_true",
                help=f"Popula apenas {option}.",
            )

    def handle(self, *args, **options):
        selected_options = {
            option for option in self.populate_options if options[option]
        }

        if options["clear"]:
            self.clear_data(selected_options or None)

        self.populate_database(selected_options or None)
        self.stdout.write(self.style.SUCCESS("População concluída com sucesso."))

    def clear_data(self, selected_options: set[str] | None = None) -> None:
        self.stdout.write("Removendo dados existentes...")
        if selected_options is None:
            OrderStatusHistory.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Address.objects.all().delete()
            Review.objects.all().delete()
            Stock.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Dados existentes removidos."))
            return

        if "order" in selected_options:
            OrderStatusHistory.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
        if "address" in selected_options:
            Address.objects.all().delete()
        if "review" in selected_options:
            Review.objects.all().delete()
        if "stock" in selected_options:
            Stock.objects.all().delete()
        if "product" in selected_options:
            Product.objects.all().delete()
        if "category" in selected_options:
            Category.objects.all().delete()
        if "tag" in selected_options:
            Tag.objects.all().delete()
        if "user" in selected_options:
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Dados existentes removidos."))

    @transaction.atomic
    def populate_database(self, selected_options: set[str] | None = None) -> None:
        fake = Faker("pt_BR")
        should_run_all = selected_options is None
        needs_products = should_run_all or bool(
            selected_options & {"product", "stock", "order", "review"}
        )
        needs_users = should_run_all or bool(
            selected_options & {"user", "address", "order", "review"}
        )
        needs_addresses = should_run_all or bool(
            selected_options & {"address", "order"}
        )

        if should_run_all or "category" in selected_options:
            self.stdout.write("Gerando categorias...")
            categories = self.create_categories()
        elif "product" in selected_options:
            categories = self.require_records(Category, "categorias", "--product")
        else:
            categories = []

        if should_run_all or "tag" in selected_options:
            self.stdout.write("Gerando tags...")
            tags = self.create_tags()
        elif "product" in selected_options:
            tags = self.require_records(Tag, "tags", "--product")
        else:
            tags = []

        if should_run_all or "product" in selected_options:
            self.stdout.write("Gerando produtos...")
            products = self.create_products(categories, tags, fake)
        elif needs_products:
            products = self.require_records(
                Product,
                "produtos",
                "--stock/--order/--review",
            )
        else:
            products = []

        if should_run_all or "stock" in selected_options:
            self.stdout.write("Gerando estoque...")
            self.create_stock(products)

        if should_run_all or "user" in selected_options:
            self.stdout.write("Gerando usuários...")
            users = self.create_users(fake)
        elif needs_users:
            users = self.require_records(
                User.objects.filter(is_superuser=False),
                "usuários",
                "--address/--order/--review",
            )
        else:
            users = []

        if should_run_all or "address" in selected_options:
            self.stdout.write("Gerando endereços...")
            addresses = self.create_addresses(users, fake)
        elif needs_addresses:
            addresses = self.require_records(Address, "endereços", "--order")
        else:
            addresses = []

        if should_run_all or "order" in selected_options:
            self.stdout.write("Gerando pedidos, itens e status...")
            self.create_orders(users, addresses, products)

        if should_run_all or "review" in selected_options:
            self.stdout.write("Gerando reviews...")
            self.create_reviews(products, users)

    def require_records(self, source, record_name: str, option_name: str) -> list:
        queryset = source.objects.all() if hasattr(source, "objects") else source
        records = list(queryset)
        if not records:
            raise CommandError(
                f"Não existem {record_name} para popular {option_name}. "
                "Popule as dependências primeiro ou rode o populate completo."
            )
        return records

    def create_categories(self) -> list[Category]:
        category_names = [
            "Eletrônicos",
            "Livros",
            "Moda",
            "Beleza",
            "Esportes",
            "Casa",
            "Brinquedos",
            "Alimentos",
            "Saúde",
            "Automotivo",
        ]

        categories = [Category(name=name) for name in category_names]
        Category.objects.bulk_create(categories)

        created = list(Category.objects.all())
        for index, category in enumerate(created):
            if index >= 5:
                category.parent = created[index - 5]
                category.save(update_fields=["parent"])

        return list(Category.objects.all())

    def create_tags(self) -> list[Tag]:
        tag_names = [
            "Novo",
            "Mais vendido",
            "Promoção",
            "Premium",
            "Sustentável",
            "Popular",
            "Exclusivo",
            "Recomendado",
            "Clássico",
            "Edição limitada",
        ]
        tags = [Tag(name=name) for name in tag_names]
        Tag.objects.bulk_create(tags)
        return list(Tag.objects.all())

    def create_products(
        self,
        categories: list[Category],
        tags: list[Tag],
        fake: Faker,
    ) -> list[Product]:
        brands = [
            "NovaTech",
            "Lumi",
            "Atlas",
            "Verde",
            "Eclipse",
            "Aurora",
            "Pulse",
            "Globo",
            "Mistral",
            "Viva",
        ]
        adjectives = [
            "Smart",
            "Premium",
            "Avançado",
            "Compacto",
            "Econômico",
            "Essencial",
            "Durável",
            "Elegante",
            "Profissional",
            "Portátil",
        ]
        nouns_by_category = {
            "Eletrônicos": [
                "Fone",
                "Carregador",
                "Smartphone",
                "Tablet",
                "Câmera",
                "Roteador",
                "Monitor",
                "Notebook",
            ],
            "Livros": [
                "Manual",
                "Guia",
                "Romance",
                "Edição",
                "Coleção",
                "Best-seller",
            ],
            "Moda": [
                "Jaqueta",
                "Camisa",
                "Relógio",
                "Bolsa",
                "Tênis",
                "Calça",
            ],
            "Beleza": [
                "Perfume",
                "Creme",
                "Batom",
                "Shampoo",
                "Kit",
                "Máscara",
            ],
            "Esportes": [
                "Bola",
                "Mochila",
                "Camiseta",
                "Rede",
                "Tênis",
                "Short",
            ],
            "Casa": [
                "Vaso",
                "Toalha",
                "Luminária",
                "Jogo",
                "Tapete",
                "Móvel",
            ],
            "Brinquedos": [
                "Boneca",
                "Carrinho",
                "Quebra-cabeça",
                "Jogo",
                "Urso",
                "Figura",
            ],
            "Alimentos": [
                "Kit",
                "Caixa",
                "Cesta",
                "Combo",
                "Lanche",
                "Chocolate",
            ],
            "Saúde": [
                "Suplemento",
                "Termômetro",
                "Banda",
                "Creme",
                "Máscara",
                "Kit",
            ],
            "Automotivo": [
                "Capa",
                "Óleo",
                "Filtro",
                "Lanterna",
                "Bateria",
                "Acessório",
            ],
        }

        products = []
        product_templates = {
            "Eletrônicos": [
                "{brand} Celular {model}",
                "{brand} Televisão {size}''",
                "{brand} {noun} {model}",
                "{brand} {noun} {model}",
            ],
            "Livros": [
                "{brand} {noun} {model}",
                "{noun} {model}",
                "{brand} {noun} de {subtitle}",
            ],
            "Moda": [
                "{brand} {noun} {model}",
                "{brand} {noun} {size}",
            ],
            "Beleza": [
                "{brand} {noun} {model}",
                "{brand} Kit {noun} {model}",
            ],
            "Esportes": [
                "{brand} {noun} {model}",
                "{brand} {noun} {size}",
            ],
            "Casa": [
                "{brand} {noun} {model}",
                "{brand} {noun} {size}",
            ],
            "Brinquedos": [
                "{brand} {noun} {model}",
                "{brand} {noun} {model}",
            ],
            "Alimentos": [
                "{brand} {noun} {model}",
                "{brand} {noun} {size}",
            ],
            "Saúde": [
                "{brand} {noun} {model}",
                "{brand} {noun} {size}",
            ],
            "Automotivo": [
                "{brand} {noun} {model}",
                "{brand} {noun} {size}V",
            ],
        }

        models_by_category = {
            "Eletrônicos": ["S34", "S56", "X10", "X20", "G7"],
            "Livros": [
                "Vol. 1",
                "Vol. 2",
                "Edição Especial",
                "Coleção 2026",
                "Tomo Único",
            ],
            "Moda": ["S34", "M42", "L44", "XL46", "Plus"],
            "Beleza": ["2026", "Edição Luxo", "Essência", "Toque", "Soft"],
            "Esportes": ["Pro", "Elite", "Turbo", "Max", "Fit"],
            "Casa": ["Deluxe", "Clássico", "Essencial", "Premium", "Compact"],
            "Brinquedos": ["Series 3", "Edition", "Play", "Fun", "Starter"],
            "Alimentos": ["Pack", "Family", "Select", "Premium", "Box"],
            "Saúde": ["Plus", "Care", "Active", "Repair", "Safe"],
            "Automotivo": ["V1", "X2", "Turbo", "Sport", "Pro"],
        }
        products = []
        for _ in range(100):
            category = random.choice(categories)
            brand = random.choice(brands)
            noun = random.choice(nouns_by_category.get(category.name, ["Produto"]))
            size = random.choice([32, 43, 50, 55, 65])
            model = random.choice(models_by_category.get(category.name, ["S34"]))
            subtitle = fake.word().title()
            template = random.choice(
                product_templates.get(category.name, ["{brand} {noun} {model}"])
            )
            name = template.format(
                brand=brand,
                noun=noun,
                model=model,
                size=size,
                subtitle=subtitle,
            )
            price = Decimal(str(round(random.uniform(25.0, 1200.0), 2)))
            products.append(Product(name=name, category=category, price=price))

        Product.objects.bulk_create(products)
        created_products = list(Product.objects.all())

        tags_per_product = min(3, len(tags))
        for product in created_products:
            tags_for_product = random.sample(tags, k=tags_per_product)
            product.tags.add(*tags_for_product)

        return created_products

    def create_stock(self, products: list[Product]) -> None:
        products_with_stock = set(
            Stock.objects.filter(product__in=products).values_list(
                "product_id",
                flat=True,
            )
        )
        stock_entries = [
            Stock(product=product, quantity=random.randint(10, 400))
            for product in products
            if product.id not in products_with_stock
        ]
        Stock.objects.bulk_create(stock_entries)

    def create_users(self, fake: Faker) -> list[User]:
        users = []
        for _ in range(1000):
            username = fake.unique.user_name()
            email = fake.unique.email()
            user = User(
                username=username,
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            user.set_password("password123")
            users.append(user)

        User.objects.bulk_create(users)
        return list(User.objects.filter(is_superuser=False))

    def create_addresses(self, users: list[User], fake: Faker) -> list[Address]:
        addresses = []
        for user in users:
            for _ in range(3):
                addresses.append(
                    Address(
                        user=user,
                        street=fake.street_address(),
                        city=fake.city(),
                    )
                )

        Address.objects.bulk_create(addresses)
        return list(Address.objects.all())

    def create_orders(
        self,
        users: list[User],
        addresses: list[Address],
        products: list[Product],
    ) -> None:
        addresses_by_user: dict[int, list[Address]] = {}
        for address in addresses:
            addresses_by_user.setdefault(address.user_id, []).append(address)

        orders = []
        for user in users:
            user_addresses = addresses_by_user.get(user.id, [])
            for _ in range(10):
                orders.append(
                    Order(
                        user=user,
                        address=random.choice(user_addresses),
                    )
                )

        Order.objects.bulk_create(orders)
        created_orders = list(Order.objects.all())

        order_items = []
        items_per_order = min(5, len(products))
        for order in created_orders:
            chosen_products = random.sample(products, k=items_per_order)
            for product in chosen_products:
                order_items.append(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=random.randint(1, 4),
                    )
                )

        OrderItem.objects.bulk_create(order_items)

        status_sequence = [
            "Pendente",
            "Aprovado",
            "Em preparação",
            "Enviado",
            "Entregue",
        ]
        status_histories = []
        for order in created_orders:
            for status in status_sequence:
                status_histories.append(OrderStatusHistory(order=order, status=status))

        OrderStatusHistory.objects.bulk_create(status_histories)

    def create_reviews(self, products: list[Product], users: list[User]) -> None:
        products_with_counts = Product.objects.filter(
            id__in=[product.id for product in products]
        ).annotate(review_count=Count("reviews"))

        reviews = []
        for product in products_with_counts:
            reviews_to_create = max(0, 10 - product.review_count)
            if reviews_to_create == 0:
                continue

            selected_users = (
                random.sample(users, k=reviews_to_create)
                if len(users) >= reviews_to_create
                else random.choices(users, k=reviews_to_create)
            )
            for user in selected_users:
                reviews.append(
                    Review(
                        product=product,
                        user=user,
                        rating=random.randint(1, 5),
                    )
                )

        Review.objects.bulk_create(reviews)
