from dto import UsuarioDTO
from typing import List

class UsuarioDAO:
    def __init__(self, connection):
        self.connection = connection
        
    def obtener_todas_los_usuarios(self) -> List[UsuarioDTO]:
        try: 
            cursor = self.connection.cursor()
            cursor.execute("""
                        SELECT id_empleado, nombre_usuario, email, contraseña, rol
                        FROM Usuario
                    """)   
            filas = cursor.fetchall()
            usuarios = [UsuarioDTO(*fila) for fila in filas]
            cursor.close()
            return usuarios
        except Exception as e:
            return []
        
    def buscar_por_nombre_usuario(self, nombre_usuario: str) -> UsuarioDTO:
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT id_empleado, nombre_usuario, email, contraseña, rol
                FROM Usuario
                WHERE nombre_usuario = :nombre_usuario
            """
            cursor.execute(query, {'nombre_usuario': nombre_usuario.upper()})
            result = cursor.fetchone()
            
            if result:
                return UsuarioDTO(*result) if result else None
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

    def _insertar_usuario(self, usuario_dto: UsuarioDTO) -> bool:
        """Insertar el nuevo usuario en la base de datos."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Usuario (id_empleado, nombre_usuario, email, contraseña, rol)
                VALUES (:1, :2, :3, :4, :5)
            """, (usuario_dto.id_empleado, usuario_dto.nombre_usuario, usuario_dto.email, usuario_dto.contraseña, usuario_dto.rol))
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()  # Revertir la transacción en caso de error
            print(f"Error al insertar el usuario: {e}")
            return False
        finally:
            cursor.close()

    def insertar_usuario(self, usuario_dto: UsuarioDTO) -> bool:
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
            print(id_empleado)
            cursor.execute("DELETE FROM Usuario WHERE id_empleado = :1", (id_empleado,))
            self.connection.commit()
            print("Hola")
        except Exception as e:
            self.connection.rollback()  # Revertir en caso de error
            raise e
        finally:
            cursor.close()

    def buscar_usuarios(self, emp_id=None, nombre=None, email=None, rol=None) -> List[UsuarioDTO]:
        query = "SELECT id_empleado, nombre_usuario, email, contraseña, rol FROM Usuario WHERE 1=1"
        parameters = []

        if emp_id:
            query += " AND id_empleado LIKE :1"
            parameters.append(f"%{emp_id}%")
        if nombre:
            query += " AND UPPER(nombre_usuario) LIKE :2"
            parameters.append(f"%{nombre.upper()}%")
        if email:
            query += " AND UPPER(email) LIKE :3"
            parameters.append(f"%{email.upper()}%")
        if rol:
            query += " AND rol LIKE :4"
            parameters.append(rol)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            filas = cursor.fetchall()
            usuarios = [UsuarioDTO(*fila) for fila in filas]
            cursor.close()
            return usuarios
        except Exception as e:
            return []