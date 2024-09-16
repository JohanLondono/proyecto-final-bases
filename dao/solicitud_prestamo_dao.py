from dto import SolicitudPrestamoDTO
from typing import List

class SolicitudPrestamoDAO:
    def __init__(self, connection):
        self.connection = connection

    def insertar_solicitud_prestamo(self, solicitud: SolicitudPrestamoDTO):
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO SolicitudPrestamo (id_empleado, monto, periodo, interes, fecha_solicitud, estado)
                VALUES (:id_empleado, :monto, :periodo, :interes, :fecha_solicitud, :estado)
            """
            
            # Convertir la fecha_solicitud al formato adecuado (YYYY-MM-DD HH24:MI:SS)
            fecha_solicitud = solicitud.fecha_solicitud
            cursor.execute(query, {
                'id_empleado': solicitud.id_empleado,
                'monto': float(solicitud.monto),
                'periodo': int(solicitud.periodo),
                'interes': float(solicitud.interes),
                'fecha_solicitud': fecha_solicitud,
                'estado': solicitud.estado
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al insertar solicitud de préstamo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def cargar_todas_las_solicitudes_prestamos(self) -> List[SolicitudPrestamoDTO]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, id_empleado, monto, periodo, interes, fecha_solicitud, estado FROM SolicitudPrestamo")
            filas = cursor.fetchall()
            solicitudes_prestamos = [SolicitudPrestamoDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(f"Error al cargar todas las solicitudes de préstamos: {e}")
            return []

    def cargar_solicitudes_prestamos_por_id_empleado(self, id_empleado) -> List[SolicitudPrestamoDTO]:

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, id_empleado, monto, periodo, interes, fecha_solicitud, estado
                FROM SolicitudPrestamo
                WHERE id_empleado = :1
            """, (id_empleado,))
            filas = cursor.fetchall()
            solicitudes_prestamos = [SolicitudPrestamoDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(f"Error al buscar solicitudes de préstamo para el empleado con ID {id_empleado}: {e}")
            return []

    def cargar_solicitud_por_id(self, id_solicitud_prestamo) -> SolicitudPrestamoDTO:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, id_empleado, monto, periodo, interes, fecha_solicitud, estado FROM SolicitudPrestamo WHERE id = :1", (id_solicitud_prestamo,))
            fila = cursor.fetchone()
            cursor.close()
            return SolicitudPrestamoDTO(*fila) if fila else None
        except Exception as e:
            print(f"Error al cargar la solicitud de préstamo con ID {id_solicitud_prestamo}: {e}")
            return None

    def buscar_solicitudes_prestamos(self, id_solicitud=None, id_empleado=None, estado=None, fecha_inicio=None, fecha_fin=None):
        consulta = "SELECT id, id_empleado, monto, periodo, interes, fecha_solicitud, estado FROM SolicitudPrestamo WHERE 1=1"
        parametros = []

        if id_solicitud:
            consulta += " AND id = :1"
            parametros.append(id_solicitud)
        if id_empleado:
            consulta += " AND id_empleado = :2"
            parametros.append(id_empleado)
        if estado:
            consulta += " AND estado = :3"
            parametros.append(estado)
        if fecha_inicio and fecha_fin:
            consulta += " AND fecha_solicitud BETWEEN :4 AND :5"
            parametros.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            consulta += " AND fecha_solicitud >= :4"
            parametros.append(fecha_inicio)
        elif fecha_fin:
            consulta += " AND fecha_solicitud <= :4"
            parametros.append(fecha_fin)


        try:
            cursor = self.connection.cursor()
            cursor.execute(consulta, parametros)
            filas = cursor.fetchall()
            solicitudes_prestamos = [SolicitudPrestamoDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            return []

    def actualizar_estado_solicitud(self, id_solicitud_prestamo, nuevo_estado):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE SolicitudPrestamo SET estado = :1 WHERE id = :2", (nuevo_estado, id_solicitud_prestamo))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            raise e

    def cancelar_solicitud_prestamo_por_id(self, id_solicitud_prestamo):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE SolicitudPrestamo SET estado = 'CANCELADA' WHERE id = :1", (id_solicitud_prestamo,))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            raise e
