from dto import TipoCargoDTO
from typing import List

class TipoCargoDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_tipo_cargo(self, tipo_cargo_dto: TipoCargoDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO TipoCargo (nombre, salario, tope_salario)
                VALUES (:nombre, :salario, :tope_salario)
            """
            cursor.execute(query, {
                'meses': tipo_cargo_dto.nombre,
                'interes': tipo_cargo_dto.salario,
                'tope_salario': tipo_cargo_dto.tope_salario
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el tipo de cargo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_tipo_cargos(self) -> List[TipoCargoDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre, salario, tope_salario
            FROM 
                TipoCargo
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [TipoCargoDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos tipos de cargos: {e}")
            return []

    def obtener_tipo_cargo_por_nombre(self, nombre: str) -> TipoCargoDTO:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre, salario, tope_salario
            FROM 
                TipoCargo
            WHERE nombre = :1
            """
            cursor.execute(query, (nombre,))
            fila = cursor.fetchone()

            cursor.close()

            return TipoCargoDTO(*fila) if fila else None

        except Exception as e:
            print(f"Error al obtener el tipo de cargo {nombre}: {e}")
            raise e