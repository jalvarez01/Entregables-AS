import datetime

from ..domain.interfaces import ProcesadorPago


class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.

    Simula un banco local dejando rastro en un archivo de log. El servicio que
    lo usa no sabe que esto es un archivo: para él es solo alguien que cumple
    el contrato ProcesadorPago.
    """

    # El nombre incluye la identidad del estudiante para que la evidencia de
    # ejecución sea única (requisito del tutorial).
    ARCHIVO_LOG = "pagos_locales_JUAN_JOSE_ALVAREZ.log"

    def pagar(self, monto: float) -> bool:
        with open(self.ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.datetime.now()}] BANCO NACIONAL - "
                f"Transaccion exitosa por: ${monto}\n"
            )
        return True
