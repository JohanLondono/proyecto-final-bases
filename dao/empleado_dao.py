from dto import EmpleadoDTO
from typing import List

class EmpleadoDAO:
    def __init__(self, connection):
        self.connection = connection

    def obtener_todos_los_empleados(self) -> List[EmpleadoDTO]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id_empleado, nombre, apellido, sucursal_codigo, puesto, salario FROM Empleado")
            filas = cursor.fetchall()
            empleados = [EmpleadoDTO(*fila) for fila in filas]
            cursor.close()
            return empleados
        except Exception as e:
            return []
        
    def obtener_empleado_por_id(self, id_empleado) -> EmpleadoDTO:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id_empleado, 
                nombre, 
                apellido, 
                sucursal_codigo, 
                puesto, 
                salario
            FROM 
                Empleado
            WHERE 
                id_empleado = :id_empleado
            """
            cursor.execute(query, {"id_empleado": id_empleado})
            fila = cursor.fetchone()
            empleado = EmpleadoDTO(*fila) if fila else None
            cursor.close()
            return empleado
        except Exception as e:
            print(e) 

    def insertar_empleado(self, empleado: EmpleadoDTO):
        cursor = self.connection.cursor()
        emp_id = empleado.id_empleado
        try:
            # Consultar si el ID del empleado ya está registrado
            cursor.execute("SELECT COUNT(*) FROM Empleado WHERE id_empleado = :1", (emp_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                # El ID ya está en uso, mostrar un mensaje de error o manejar el caso
                return False  # Indicar que la inserción falló porque ya existe el empleado
            else:
                cursor.execute("""
                INSERT INTO Empleado (id_empleado, nombre, apellido, sucursal_codigo, puesto, salario)
                VALUES (:1, :2, :3, :4, :5, :6)""",
                (empleado.id_empleado, empleado.nombre, empleado.apellido, empleado.sucursal_codigo, empleado.puesto, empleado.salario))
                self.connection.commit()
                return True  # Indicar que la inserción fue exitosa
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def eliminar_empleado(self, id_empleado):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM Empleado WHERE id_empleado = :1", (id_empleado,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def buscar_empleados(self, id_empleado=None, nombre=None, apellido=None, sucursal_codigo=None, puesto=None):
        query = "SELECT id_empleado, nombre, apellido, sucursal_codigo, puesto, salario FROM Empleado WHERE 1=1"
        parameters = []
        if id_empleado:
            query += " AND id_empleado LIKE :1"
            parameters.append(f"%{id_empleado}%")
        if nombre:
            query += " AND UPPER(nombre) LIKE :2"
            parameters.append(f"%{nombre.upper()}%")
        if apellido:
            query += " AND UPPER(apellido) LIKE :3"
            parameters.append(f"%{apellido.upper()}%")
        if sucursal_codigo:
            query += " AND UPPER(sucursal_codigo) LIKE :4"
            parameters.append(f"%{sucursal_codigo.upper()}%")
        if puesto:
            query += " AND puesto = :5"
            parameters.append(puesto)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            filas = cursor.fetchall()
            empleados = [EmpleadoDTO(*fila) for fila in filas]
            cursor.close()
            return empleados
        except Exception as e:
            return []