from dto import EmpleadoSqlDTO
from dto import EmpleadoTablaDTO
from typing import List

class EmpleadoDAO:
    def __init__(self, connection):
        self.connection = connection

    def obtener_todos_los_empleados(self) -> List[EmpleadoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                e.id_empleado, 
                e.nombre,         
                e.apellido, 
                e.sucursal_codigo, 
                tc.nombre AS puesto,  
                tc.salario 
            FROM 
                Empleado e
            JOIN 
                TipoCargo tc ON e.id_tipo_cargo = tc.id
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            empleados = [EmpleadoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return empleados
        except Exception as e:
            return []
        
    def obtener_empleado_por_id(self, id_empleado) -> EmpleadoTablaDTO:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                e.id_empleado, 
                e.nombre,         
                e.apellido, 
                e.sucursal_codigo, 
                tc.nombre AS puesto,  
                tc.salario 
            FROM 
                Empleado e
            JOIN 
                TipoCargo tc ON e.id_tipo_cargo = tc.id
            WHERE 
                e.id_empleado = :id_empleado
            """
            cursor.execute(query, {"id_empleado": id_empleado})
            fila = cursor.fetchone()
            empleado = EmpleadoTablaDTO(*fila) if fila else None
            cursor.close()
            return empleado
        except Exception as e:
            print(e) 

    def insertar_empleado(self, empleado: EmpleadoSqlDTO):
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
                INSERT INTO Empleado (id_empleado, nombre, apellido, sucursal_codigo, id_tipo_cargo)
                VALUES (:1, :2, :3, :4, :5)""",
                (empleado.id_empleado, empleado.nombre, empleado.apellido, empleado.sucursal_codigo, empleado.id_tipo_cargo))
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

    def buscar_empleados(self, id_empleado=None, nombre=None, apellido=None, sucursal_codigo=None, id_tipo_cargo=None) -> List[EmpleadoTablaDTO]:
        query = """
        SELECT 
            e.id_empleado, 
            e.nombre,         
            e.apellido, 
            e.sucursal_codigo, 
            tc.nombre AS puesto,  
            tc.salario 
        FROM 
            Empleado e
        JOIN 
            TipoCargo tc ON e.id_tipo_cargo = tc.id
        WHERE 1=1
        """
        parameters = []
        if id_empleado:
            query += " AND e.id_empleado = :1"
            parameters.append(f"{id_empleado}")
        if nombre:
            query += " AND UPPER(e.nombre) LIKE :2"
            parameters.append(f"%{nombre.upper()}%")
        if apellido:
            query += " AND UPPER(e.apellido) LIKE :3"
            parameters.append(f"%{apellido.upper()}%")
        if sucursal_codigo:
            query += " AND UPPER(e.sucursal_codigo) LIKE :4"
            parameters.append(f"%{sucursal_codigo.upper()}%")
        if id_tipo_cargo:
            query += " AND e.id_tipo_cargo = :5"
            parameters.append(f"{id_tipo_cargo}")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            filas = cursor.fetchall()
            empleados = [EmpleadoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return empleados
        except Exception as e:
            print(e)
            return []