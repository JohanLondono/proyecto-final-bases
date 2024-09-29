from dto import TipoPagoDTO
from typing import List

class TipoPagoDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_tipo_pago(self, tipo_pago_dto: TipoPagoDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO TipoPago (nombre)
                VALUES (:nombre)
            """
            cursor.execute(query, {
                'nombre': tipo_pago_dto.nombre
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el tipo de pago: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_tipos_pago(self) -> List[TipoPagoDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre
            FROM 
                TipoPago
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [TipoPagoDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los tipos pagos: {e}")
            return []

    