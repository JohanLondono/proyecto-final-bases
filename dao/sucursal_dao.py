from dto import SucursalDTO
from typing import List

class SucursalDAO:
    def __init__(self, connection):
        self.connection = connection

    def obtener_todas_las_sucursales(self) -> List[SucursalDTO]:
        try: 
            cursor = self.connection.cursor()
            cursor.execute("SELECT codigo, nombre, departamento, municipio, director, presupuesto FROM Sucursal")
            filas = cursor.fetchall()
            sucursales = [SucursalDTO(*fila) for fila in filas]
            cursor.close()

            return sucursales
        except Exception as e:
            print(f"Error al recuperar las Sucursales: {e}")
            return []
        
    def insertar_sucursal(self, sucursal: SucursalDTO):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Sucursal (codigo, nombre, departamento, municipio, director, presupuesto)
                VALUES (:1, :2, :3, :4, :5, :6)""",
                (sucursal.codigo, sucursal.nombre, sucursal.departamento, sucursal.municipio, sucursal.director, sucursal.presupuesto))
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

    def buscar_sucursales(self, codigo=None, nombre=None, departamento=None, municipio=None) -> List[SucursalDTO]:
        query = "SELECT codigo, nombre, departamento, municipio, director, presupuesto FROM Sucursal WHERE 1=1"
        parameters = []

        if codigo:
            query += " AND codigo LIKE :1"
            parameters.append(f"%{codigo}%")
        if nombre:
            query += " AND UPPER(nombre) LIKE :2"
            parameters.append(f"%{nombre.upper()}%")
        if departamento:
            query += " AND UPPER(departamento) LIKE :3"
            parameters.append(f"%{departamento.upper()}%")
        if municipio:
            query += " AND UPPER(municipio) LIKE :4"
            parameters.append(f"%{municipio.upper()}%")
        try: 
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            filas = cursor.fetchall()

            sucursales = [SucursalDTO(*fila) for fila in filas]
            cursor.close()

            return sucursales
        except Exception as e:
            print(f"Error al recuperar las Sucursales: {e}")
            return []