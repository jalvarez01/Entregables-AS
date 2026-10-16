"""
Carga libros de prueba si la base está vacía.

En Docker y en AWS la base de PostgreSQL arranca vacía; sin datos, los
endpoints de compra no tienen qué vender. El comando es idempotente: si ya hay
libros, no hace nada, así se puede correr en cada arranque del contenedor.

Uso:
    python manage.py cargar_demo
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from tienda_app.models import Inventario, Libro

LIBROS = [
    ("Clean Code en Python", "150.00", 10),
    ("Refactoring", "210.00", 10),
    ("Domain-Driven Design", "185.50", 10),
]


class Command(BaseCommand):
    help = "Crea libros con inventario si todavía no hay ninguno."

    @transaction.atomic
    def handle(self, *args, **options):
        if Libro.objects.exists():
            self.stdout.write("Ya hay libros cargados, no se crea nada.")
            return

        for titulo, precio, cantidad in LIBROS:
            libro = Libro.objects.create(titulo=titulo, precio=precio)
            Inventario.objects.create(libro=libro, cantidad=cantidad)

        self.stdout.write(self.style.SUCCESS(f"Creados {len(LIBROS)} libros con inventario."))
