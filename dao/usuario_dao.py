from dto import UsuarioSqlDTO
from dto import UsuarioTablaDTO
from typing import List

class UsuarioDAO:
    def __init__(self, connection):
        self.connection = connection
        
    def obtener_todas_los_usuarios(self) -> List[UsuarioTablaDTO]:
        try: 
            cursor = self.connection.cursor()
            cursor.execute("""
                        SELECT u.id_empleado, u.nombre_usuario, u.email, u.contraseña, tpu.nombre AS rol
                        FROM Usuario u
                        JOIN TipoUsuario tpu ON u.id_tipo_usuario = tpu.id
                    """)   
            filas = cursor.fetchall()
            usuarios = [UsuarioTablaDTO(*fila) for fila in filas]
            cursor.close()
            return usuarios
        except Exception as e:
            return []
        
    def buscar_por_nombre_usuario(self, nombre_usuario: str) -> UsuarioTablaDTO:
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT u.id_empleado, u.nombre_usuario, u.email, u.contraseña, tpu.nombre AS rol
                FROM Usuario u
                JOIN TipoUsuario tpu ON u.id_tipo_usuario = tpu.id
                WHERE u.nombre_usuario = :nombre_usuario
            """
            cursor.execute(query, {'nombre_usuario': nombre_usuario.upper()})
            result = cursor.fetchone()
            
            if result:
                return UsuarioTablaDTO(*result) if result else None
            else:
                return None  # Usuario no encontrado
        except Exception as e:
            print(f"Error al buscar el usuario: {e}")
        finally:
            cursor.close()
    
    def _verificar_nombre_usuario_existe(self, nombre_usuario: str) -> bool:
        """Verificar si el nombre de usuario ya existe en la base de datos."""
        cursor = self.connection.cursor()
        try:
            nombre_usuario_upper = nombre_usuario.upper()
            cursor.execute("""
                SELECT COUNT(*)
                FROM Usuario
                WHERE UPPER(nombre_usuario) = :1
            """, (nombre_usuario_upper,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error al verificar el nombre de usuario: {e}")
            return False
        finally:
            cursor.close()

    def verificar_administrador_existe(self) -> bool:
        """Verificar si el nombre de usuario ya existe en la base de datos."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM Usuario
                WHERE id_tipo_usuario = 1
            """)
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error al verificar el usuario administrador: {e}")
            return False
        finally:
            cursor.close()

    def _verificar_empleado_tiene_usuario(self, id_empleado: int) -> bool:
        """Verificar si el empleado ya tiene un usuario asociado."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM Usuario WHERE id_empleado = :1", (id_empleado,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error al verificar el usuario del empleado: {e}")
            return False
        finally:
            cursor.close()

    def _insertar_usuario(self, usuario_dto: UsuarioSqlDTO) -> bool:
        """Insertar el nuevo usuario en la base de datos."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Usuario (id_empleado, nombre_usuario, email, contraseña, id_tipo_usuario)
                VALUES (:1, :2, :3, :4, :5)
            """, (usuario_dto.id_empleado, usuario_dto.nombre_usuario, usuario_dto.email, usuario_dto.contraseña, usuario_dto.id_tipo_usuario))
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()  # Revertir la transacción en caso de error
            print(f"Error al insertar el usuario: {e}")
            return False
        finally:
            cursor.close()

    def insertar_usuario(self, usuario_dto: UsuarioSqlDTO) -> bool:
        """Método principal para insertar un nuevo usuario en la base de datos."""
        if self._verificar_nombre_usuario_existe(usuario_dto.nombre_usuario):
            print("Error: El nombre de usuario ya existe.")
            return False
        
        if self._verificar_empleado_tiene_usuario(usuario_dto.id_empleado):
            print("Error: El empleado ya tiene un usuario asociado.")
            return False
        
        return self._insertar_usuario(usuario_dto)

    def eliminar_usuario(self, id_empleado):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM Usuario WHERE id_empleado = :1", (id_empleado,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()  # Revertir en caso de error
            raise e
        finally:
            cursor.close()

    def buscar_usuarios(self, emp_id=None, nombre=None, email=None, id_tipo_usuario=None) -> List[UsuarioTablaDTO]:
        query = """
            SELECT u.id_empleado, u.nombre_usuario, u.email, u.contraseña, tpu.nombre AS rol
            FROM Usuario u
            JOIN TipoUsuario tpu ON u.id_tipo_usuario = tpu.id
            WHERE 1=1
        """
        parameters = []

        if emp_id:
            query += " AND u.id_empleado = :1"
            parameters.append(f"{emp_id}")
        if nombre:
            query += " AND UPPER(u.nombre_usuario) LIKE :2"
            parameters.append(f"%{nombre.upper()}%")
        if email:
            query += " AND UPPER(u.email) LIKE :3"
            parameters.append(f"%{email.upper()}%")
        if id_tipo_usuario:
            query += " AND u.id_tipo_usuario = :4"
            parameters.append(f"{id_tipo_usuario}")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            filas = cursor.fetchall()
            usuarios = [UsuarioTablaDTO(*fila) for fila in filas]
            cursor.close()
            return usuarios
        except Exception as e:
            # Manejo de excepción adecuado (puedes registrar el error o imprimirlo)
            return []