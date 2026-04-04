from fastapi import HTTPException, status

from app.repositories.inventario_repository import InventarioRepository


class InventarioService:
    def __init__(self, repository: InventarioRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def get(self, repuesto_id: int):
        item = self.repository.get(repuesto_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repuesto no encontrado")
        return item

    def create(self, payload: dict):
        return self.repository.create(payload)

    def update(self, repuesto_id: int, payload: dict):
        item = self.get(repuesto_id)
        return self.repository.update(item, payload)

    def delete(self, repuesto_id: int):
        item = self.get(repuesto_id)
        self.repository.delete(item)

    def create_movement(self, payload: dict):
        item = self.get(payload["repuesto_id"])
        movement_type = payload["tipo_movimiento"].upper()
        quantity = payload["cantidad"]

        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor a cero")

        if movement_type == "ENTRADA":
            item.stock_actual += quantity
        elif movement_type == "SALIDA":
            if item.stock_actual < quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente")
            item.stock_actual -= quantity
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de movimiento invalido")

        self.repository.update(item, {"stock_actual": item.stock_actual})
        payload["tipo_movimiento"] = movement_type
        return self.repository.create_movement(payload)

    def list_movements(self):
        return self.repository.list_movements()

    def list_alertas_stock(self):
        return self.repository.get_alertas_stock()
