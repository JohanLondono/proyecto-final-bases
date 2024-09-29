from dto import MunicipioDTO
from typing import List

class MunicipioDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_municipio(self, municipio_dto: MunicipioDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Municipio (id_departamento, nombre)
                VALUES (:id_departamento, :nombre)
            """
            cursor.execute(query, {
                'id_departamento': municipio_dto.id_departamento,
                'nombre': municipio_dto.nombre
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el municipio: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_municipios(self) -> List[MunicipioDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, id_departamento, nombre
            FROM 
                Municipio
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [MunicipioDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los municipios: {e}")
            return []
        
    def obtener_municipios_por_departamento(self, id_departamento) -> List[MunicipioDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                id, 
                id_departamento,
                nombre FROM Municipio 
            WHERE 
                id_departamento = :id_departamento
            """
            cursor.execute(query, {"id_departamento": id_departamento})
            filas = cursor.fetchall()
            pagos = [MunicipioDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los municipios de los departamentos: {e}")
            return []

    