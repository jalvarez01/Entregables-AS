from decimal import Decimal

from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro, Orden


class CompraService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio,
    la infraestructura y la base de datos.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        orden = (
            self.builder
            .con_usuario(usuario)
            .con_libro(libro)
            .con_cantidad(cantidad)
            .para_envio(direccion)
            .build()
        )

        pago_exitoso = self.procesador_pago.pagar(orden.total)
        if not pago_exitoso:
            orden.delete()
            raise Exception("La transacción fue rechazada por el banco.")

        inv.cantidad -= cantidad
        inv.save()

        return orden.total


class CompraRapidaService:
    """
    SERVICE LAYER de la Compra Rápida.

    Es el resultado de extraer todo lo que en la versión spaghetti vivía dentro
    de la vista: consultar inventario, calcular impuestos, cobrar y descontar
    stock. La vista ya no sabe nada de esto.

    Recibe el procesador de pago por constructor (Inversión de Dependencias):
    no instancia ningún banco concreto, así que en pruebas se le puede pasar
    un doble sin tocar el código del servicio.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def obtener_detalle(self, libro_id):
        """Datos para pintar la pantalla previa a la compra."""
        libro = get_object_or_404(Libro, id=libro_id)
        return {
            "libro": libro,
            "total": CalculadorImpuestos.obtener_total_con_iva(libro.precio),
        }

    def procesar(self, libro_id):
        """
        Ejecuta la compra completa.

        Lanza ValueError si no hay stock, para que la vista lo traduzca a un
        400 sin tener que conocer las reglas de negocio.
        """
        libro = get_object_or_404(Libro, id=libro_id)
        inventario = get_object_or_404(Inventario, libro=libro)

        if inventario.cantidad <= 0:
            raise ValueError("No hay existencias.")

        # El cálculo del impuesto vive en el dominio, no aquí:
        # si mañana cambia el IVA, se toca una sola clase.
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if not self.procesador_pago.pagar(total):
            raise ValueError("La transacción fue rechazada por el banco.")

        inventario.cantidad -= 1
        inventario.save()

        Orden.objects.create(libro=libro, total=Decimal(str(total)))

        return total


class InventarioService:
    """
    Consulta del inventario.

    Vive en la capa de servicio aunque sea una lectura: así ni la vista HTML
    ni la API tocan el ORM, y si mañana el stock viene de otro sistema solo
    cambia esta clase.
    """

    def libros(self):
        return Libro.objects.select_related("inventario").order_by("id")

    def listar(self):
        return [
            {
                "id": libro.id,
                "titulo": libro.titulo,
                "precio": libro.precio,
                "stock": getattr(getattr(libro, "inventario", None), "cantidad", 0),
            }
            for libro in self.libros()
        ]
