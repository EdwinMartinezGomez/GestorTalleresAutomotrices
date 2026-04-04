from app.repositories.pagos_repository import PagosRepository


class PagosService:
    def __init__(self, repository: PagosRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def create(self, payload: dict):
        return self.repository.create(payload)

    def list_ingresos_por_dia(self):
        return self.repository.list_ingresos_por_dia()
