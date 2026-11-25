from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from time import perf_counter
from urllib.parse import urlencode

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.test import Client, override_settings


@dataclass(frozen=True)
class EndpointConfig:
    name: str
    path: str
    page_sizes: tuple[int, ...]


@dataclass(frozen=True)
class StrategyConfig:
    name: str
    params: dict[str, str]


class QueryCounter:
    def __init__(self):
        self.count = 0

    def __call__(self, execute, sql, params, many, context):
        self.count += 1
        return execute(sql, params, many, context)


class Command(BaseCommand):
    help = "Executa benchmark dos endpoints da API medindo tempo e quantidade de queries."

    endpoints = (
        EndpointConfig("users", "/api/users/", (10, 50, 100, 500, 1000)),
        EndpointConfig("orders", "/api/orders/", (10, 50, 100, 500, 1000)),
        EndpointConfig("products", "/api/products/", (10, 50, 100)),
    )
    strategies = (
        StrategyConfig("none", {}),
        StrategyConfig("prefetch=true", {"prefetch": "true"}),
        StrategyConfig("select=true", {"select": "true"}),
        StrategyConfig(
            "prefetch=true&select=true",
            {"prefetch": "true", "select": "true"},
        ),
        StrategyConfig("prefetch_select=true", {"prefetch_select": "true"}),
    )
    fieldnames = (
        "endpoint",
        "strategy",
        "page_size",
        "time_ms",
        "query_count",
        "status_code",
        "response_bytes",
        "error",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default="benchmark_api",
            help="Diretório dos CSVs de saída. Padrão: benchmark_api.",
        )
        parser.add_argument(
            "--runs",
            type=int,
            default=10,
            help="Quantidade de execuções completas. Padrão: 10.",
        )
        parser.add_argument(
            "--api",
            action="append",
            choices=[endpoint.name for endpoint in self.endpoints],
            help=(
                "API que deve ser executada. Pode ser usado mais de uma vez. "
                "Opções: users, orders, products. Padrão: todas."
            ),
        )
        parser.add_argument(
            "--append",
            action="store_true",
            help=(
                "Continua preenchendo um CSV existente e pula combinações já gravadas."
            ),
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]
        runs = options["runs"]
        if runs < 1:
            raise CommandError("--runs deve ser maior ou igual a 1.")

        append = options["append"]
        endpoints = self.get_selected_endpoints(options["api"])
        client = Client(HTTP_ACCEPT="application/json", raise_request_exception=False)
        middleware = [
            item for item in settings.MIDDLEWARE if "debug_toolbar" not in item
        ]
        os.makedirs(output_dir, exist_ok=True)

        with override_settings(
            ALLOWED_HOSTS=["testserver", "localhost"],
            MIDDLEWARE=middleware,
        ):
            for run_number in range(1, runs + 1):
                output_path = os.path.join(
                    output_dir,
                    f"api_benchmark_{run_number:02d}.csv",
                )
                self.stdout.write(f"Execução {run_number}/{runs}: {output_path}")
                self.run_benchmark_file(client, output_path, append, endpoints)

        self.stdout.write(
            self.style.SUCCESS(f"{runs} CSVs gerados em: {output_dir}")
        )

    def run_benchmark_file(
        self,
        client: Client,
        output_path: str,
        append: bool,
        endpoints: tuple[EndpointConfig, ...],
    ) -> None:
        completed = self.load_completed_results(output_path) if append else set()
        file_exists = os.path.exists(output_path)
        should_write_header = (
            not append or not file_exists or os.path.getsize(output_path) == 0
        )
        open_mode = "a" if append else "w"

        with open(output_path, open_mode, newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            if should_write_header:
                writer.writeheader()

            self.print_table_header()
            for endpoint in endpoints:
                for page_size in endpoint.page_sizes:
                    for strategy in self.strategies:
                        result_key = (endpoint.path, strategy.name, page_size)
                        if result_key in completed:
                            continue

                        params = {"page_size": page_size, **strategy.params}
                        result = self.benchmark_request(
                            client,
                            endpoint.path,
                            page_size,
                            strategy,
                            params,
                        )
                        writer.writerow(result)
                        csv_file.flush()
                        self.print_table_row(result)

    def get_selected_endpoints(
        self,
        selected_apis: list[str] | None,
    ) -> tuple[EndpointConfig, ...]:
        if not selected_apis:
            return self.endpoints

        selected_names = set(selected_apis)
        return tuple(
            endpoint for endpoint in self.endpoints if endpoint.name in selected_names
        )

    def load_completed_results(self, output_path: str) -> set[tuple[str, str, int]]:
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return set()

        with open(output_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            return {
                (
                    row["endpoint"],
                    row["strategy"],
                    int(row["page_size"]),
                )
                for row in reader
                if row.get("endpoint")
                and row.get("strategy")
                and row.get("page_size")
            }

    def benchmark_request(
        self,
        client: Client,
        endpoint: str,
        page_size: int,
        strategy: StrategyConfig,
        params: dict[str, str | int],
    ) -> dict[str, str | int]:
        url = f"{endpoint}?{urlencode(params)}"
        query_counter = QueryCounter()

        start = perf_counter()
        try:
            with connection.execute_wrapper(query_counter):
                response = client.get(url)
            response_bytes = len(response.content)
            status_code = response.status_code
            error = ""
        except Exception as exc:
            response_bytes = 0
            status_code = 0
            error = f"{exc.__class__.__name__}: {exc}"

        elapsed_ms = (perf_counter() - start) * 1000

        return {
            "endpoint": endpoint,
            "strategy": strategy.name,
            "page_size": page_size,
            "time_ms": f"{elapsed_ms:.2f}",
            "query_count": query_counter.count,
            "status_code": status_code,
            "response_bytes": response_bytes,
            "error": error,
        }

    def print_table_header(self) -> None:
        self.stdout.write(
            "endpoint      | strategy                   | page_size | time_ms  | queries | status | bytes"
        )
        self.stdout.write(
            "--------------+----------------------------+-----------+----------+---------+--------+------"
        )

    def print_table_row(self, row: dict[str, str | int]) -> None:
        self.stdout.write(
            f"{str(row['endpoint']).ljust(13)} | "
            f"{str(row['strategy']).ljust(26)} | "
            f"{str(row['page_size']).rjust(9)} | "
            f"{str(row['time_ms']).rjust(8)} | "
            f"{str(row['query_count']).rjust(7)} | "
            f"{str(row['status_code']).rjust(6)} | "
            f"{str(row['response_bytes']).rjust(5)}"
        )
        if row["error"]:
            self.stderr.write(str(row["error"]))
