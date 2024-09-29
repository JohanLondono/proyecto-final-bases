from dto import TipoUsuarioDTO
from typing import List

class TipoUsuarioDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_tipo_usuario(self, tipo_usuario_dto: TipoUsuarioDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO TipoUsuario (nombre)
                VALUES (:nombre)
            """
            cursor.execute(query, {
                'nombre': tipo_usuario_dto.nombre
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el tipo de usuario: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_tipos_usuarios(self) -> List[TipoUsuarioDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, nombre
            FROM 
                TipoUsuario
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [TipoUsuarioDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los tipos de usuarios: {e}")
            return []

    