from django.shortcuts import render
from django.views import View

from .infra.factories import PaymentFactory
from .services import CompraRapidaService, CompraService, InventarioService


class CompraView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un "Portero": recibe la petición y delega al servicio.
    """

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                    'total': total,
                },
            )
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)


class CompraRapidaView(View):
    """
    CBV de Compra Rápida.

    Portero: recibe la petición, delega en el servicio y traduce el resultado
    a HTTP. Cero lógica de negocio, cero conocimiento del banco concreto.

    El `dispatch` arma el servicio una sola vez por petición; la Factory decide
    qué procesador de pago se inyecta según la variable PAYMENT_PROVIDER.
    """

    template_name = 'tienda_app/compra_rapida.html'

    def dispatch(self, request, *args, **kwargs):
        self.servicio = CompraRapidaService(PaymentFactory.get_processor())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, libro_id):
        return render(request, self.template_name, self.servicio.obtener_detalle(libro_id))

    def post(self, request, libro_id):
        try:
            return render(request, self.template_name,
                          {'mensaje_exito': self.servicio.procesar(libro_id)})
        except ValueError as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)


class InventarioView(View):
    """Muestra el stock actual. Refleja las compras hechas por HTML o por API."""

    template_name = "tienda_app/inventario.html"

    def get(self, request):
        return render(request, self.template_name, {"libros": InventarioService().listar()})
