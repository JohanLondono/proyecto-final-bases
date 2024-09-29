from dto import DepartamentoDTO
from typing import List

class DepartamentoDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_departamento(self, departamento_dto: DepartamentoDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Departamento (nombre)
                VALUES (:nombre)
            """
            cursor.execute(query, {
                'nombre': departamento_dto.nombre
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el departamento: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_departamentos(self) -> List[DepartamentoDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre
            FROM 
                Departamento
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [DepartamentoDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los departamentos: {e}")
            return []

    