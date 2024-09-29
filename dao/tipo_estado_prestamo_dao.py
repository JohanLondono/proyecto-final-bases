from dto import TipoEstadoPrestamoDTO
from typing import List

class TipoEstadoPrestamoDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_tipo_estado_prestamo(self, tipo_estado_prestamo_dto: TipoEstadoPrestamoDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO TipoEstadoPrestamo (nombre)
                VALUES (:nombre)
            """
            cursor.execute(query, {
                'nombre': tipo_estado_prestamo_dto.nombre
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el tipo de estado de prestamo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_tipos_estados_prestamo(self) -> List[TipoEstadoPrestamoDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre
            FROM 
                TipoEstadoPrestamo
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [TipoEstadoPrestamoDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los tipos de estados de prestamos: {e}")
            return []

    def obtener_id_tipo_estado_prestamo_por_nombre(self, nombre_estado: str) -> int:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT id 
            FROM TipoEstadoPrestamo
            WHERE UPPER(nombre) = UPPER(:1)
            """
            cursor.execute(query, (nombre_estado,))
            resultado = cursor.fetchone()

            cursor.close()

            if resultado:
                return resultado[0]  # Devuelve el ID del estado
            else:
                return None  # Si no se encontró el estado

        except Exception as e:
            print(f"Error al obtener el ID del estado {nombre_estado}: {e}")
            raise e