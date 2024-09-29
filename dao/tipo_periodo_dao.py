from dto import TipoPeriodoDTO
from typing import List

class TipoPeriodoDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_tipo_periodo(self, tipo_periodo_dto: TipoPeriodoDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO TipoPeriodo (meses, interes)
                VALUES (:meses, :interes)
            """
            cursor.execute(query, {
                'meses': tipo_periodo_dto.meses,
                'interes': tipo_periodo_dto.interes
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el tipo de periodo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_tipo_periodos(self) -> List[TipoPeriodoDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, meses, interes
            FROM 
                TipoPeriodo
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [TipoPeriodoDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos tipos de periodos: {e}")
            return []

    