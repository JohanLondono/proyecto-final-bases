from dto import TipoEstadoSolicitudDTO
from typing import List

class TipoEstadoSolicitudDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_tipo_estado_solicitud(self, tipo_estado_solicitud_dto: TipoEstadoSolicitudDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO TipoEstadoSolicitud (nombre)
                VALUES (:nombre)
            """
            cursor.execute(query, {
                'nombre': tipo_estado_solicitud_dto.nombre
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el tipo de estado de solicitud: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_tipos_estados_solicitud(self) -> List[TipoEstadoSolicitudDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre
            FROM 
                TipoEstadoSolicitud
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [TipoEstadoSolicitudDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los tipos de estados de solicitud: {e}")
            return []
        
    def obtener_id_tipo_estado_solicitud_por_nombre(self, nombre_estado: str) -> int:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT id 
            FROM TipoEstadoSolicitud 
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

    