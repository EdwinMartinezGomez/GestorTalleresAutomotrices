from app.repositories.historial_repository import HistorialRepository


class HistorialService:
    def __init__(self, repository: HistorialRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def create(self, payload: dict):
        return self.repository.create(payload)

    def list_historial_completo(self):
        return self.repository.list_historial_completo()
