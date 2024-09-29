from dto import SucursalSqlDTO
from dto import SucursalTablaDTO
from typing import List

class SucursalDAO:
    def __init__(self, connection):
        self.connection = connection

    def obtener_todas_las_sucursales(self) -> List[SucursalTablaDTO]:
        try: 
            cursor = self.connection.cursor()
            query = """
            SELECT 
                s.codigo, 
                s.nombre,         
                de.nombre, 
                mu.nombre, 
                s.presupuesto
            FROM 
                Sucursal s
            JOIN 
                Municipio mu ON s.id_municipio = mu.id
            JOIN
                Departamento de ON mu.id_departamento = de.id
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            sucursales = [SucursalTablaDTO(*fila) for fila in filas]
            cursor.close()

            return sucursales
        except Exception as e:
            print(f"Error al recuperar las Sucursales: {e}")
            return []
        
    def insertar_sucursal(self, sucursal: SucursalSqlDTO):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Sucursal (codigo, id_municipio, nombre, presupuesto)
                VALUES (:1, :2, :3, :4)""",
                (sucursal.codigo, sucursal.id_municipio, sucursal.nombre, sucursal.presupuesto))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def eliminar_sucursal(self, codigo):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM Sucursal WHERE codigo = :1", (codigo,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def buscar_sucursales(self, codigo=None, nombre=None, id_departamento=None, id_municipio=None) -> List[SucursalTablaDTO]:
        query = """
        SELECT 
            s.codigo, 
            s.nombre,         
            de.nombre, 
            mu.nombre, 
            s.presupuesto
        FROM 
            Sucursal s
        JOIN 
            Municipio mu ON s.id_municipio = mu.id
        JOIN
            Departamento de ON mu.id_departamento = de.id
        WHERE 1=1
        """
        parameters = []

        if codigo:
            query += " AND codigo LIKE :1"
            parameters.append(f"%{codigo}%")
        if nombre:
            query += " AND UPPER(s.nombre) LIKE :2"
            parameters.append(f"%{nombre.upper()}%")
        if id_departamento:
            query += " AND de.id = :3"
            parameters.append(f"{id_departamento}")
        if id_municipio:
            query += " AND mu.id = :4"
            parameters.append(f"{id_municipio}")
        try: 
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            filas = cursor.fetchall()

            sucursales = [SucursalTablaDTO(*fila) for fila in filas]
            cursor.close()

            return sucursales
        except Exception as e:
            print(f"Error al recuperar las Sucursales: {e}")
            return []