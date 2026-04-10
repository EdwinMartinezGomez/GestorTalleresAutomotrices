from app.core.kafka_events import publish_domain_event
from app.repositories.pagos_repository import PagosRepository


class PagosService:
    def __init__(self, repository: PagosRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def create(self, payload: dict):
        pago = self.repository.create(payload)
        publish_domain_event(
            topic_suffix="pagos",
            event_type="pago_creado",
            payload={
                "pago_id": pago.id,
                "orden_id": pago.orden_id,
                "monto_total": str(pago.monto_total),
                "metodo_pago": pago.metodo_pago,
            },
        )
        return pago

    def list_ingresos_por_dia(self):
        return self.repository.list_ingresos_por_dia()
