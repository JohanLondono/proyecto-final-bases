from dto import SolicitudPrestamoSqlDTO
from dto import SolicitudPrestamoTablaDTO
from .tipo_estado_solicitud_dao import TipoEstadoSolicitudDAO
from typing import List

class SolicitudPrestamoDAO:
    def __init__(self, connection):
        self.connection = connection
        self.tipo_estado_solicitud_dao = TipoEstadoSolicitudDAO(self.connection)

    def insertar_solicitud_prestamo(self, solicitud: SolicitudPrestamoSqlDTO):
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO SolicitudPrestamo (id_empleado, monto, id_tipo_periodo, fecha_solicitud, id_tipo_estado_solicitud)
                VALUES (:id_empleado, :monto, :id_tipo_periodo, :fecha_solicitud, :id_tipo_estado_solicitud)
            """
            
            # Convertir la fecha_solicitud al formato adecuado (YYYY-MM-DD HH24:MI:SS)
            fecha_solicitud = solicitud.fecha_solicitud
            cursor.execute(query, {
                'id_empleado': solicitud.id_empleado,
                'monto': float(solicitud.monto),
                'id_tipo_periodo': int(solicitud.id_tipo_periodo),
                'fecha_solicitud': fecha_solicitud,
                'id_tipo_estado_solicitud': int(solicitud.id_tipo_estado_solicitud)
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al insertar solicitud de préstamo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def cargar_todas_las_solicitudes_prestamos(self) -> List[SolicitudPrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                sp.id, 
                sp.id_empleado, 
                sp.monto, 
                tp.meses as periodo, 
                tp.interes, 
                sp.fecha_solicitud, 
                tes.nombre as estado
            FROM 
                SolicitudPrestamo sp
            JOIN 
                TipoPeriodo tp ON sp.id_tipo_periodo = tp.id
            JOIN
                TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            solicitudes_prestamos = [SolicitudPrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(f"Error al cargar todas las solicitudes de préstamos: {e}")
            return []

    def cargar_solicitudes_prestamos_por_id_empleado(self, id_empleado) -> List[SolicitudPrestamoTablaDTO]:

        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                sp.id, 
                sp.id_empleado, 
                sp.monto, 
                tp.meses as periodo, 
                tp.interes, 
                sp.fecha_solicitud, 
                tes.nombre as estado
            FROM 
                SolicitudPrestamo sp
            JOIN 
                TipoPeriodo tp ON sp.id_tipo_periodo = tp.id
            JOIN
                TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
            WHERE sp.id_empleado = :1
            """
            cursor.execute(query, (id_empleado,))
            filas = cursor.fetchall()
            solicitudes_prestamos = [SolicitudPrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(f"Error al buscar solicitudes de préstamo para el empleado con ID {id_empleado}: {e}")
            return []

    def cargar_solicitud_por_id(self, id_solicitud_prestamo) -> SolicitudPrestamoTablaDTO:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                sp.id, 
                sp.id_empleado, 
                sp.monto, 
                tp.meses as periodo, 
                tp.interes, 
                sp.fecha_solicitud, 
                tes.nombre as estado
            FROM 
                SolicitudPrestamo sp
            JOIN 
                TipoPeriodo tp ON sp.id_tipo_periodo = tp.id
            JOIN
                TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
            WHERE sp.id = :1
            """
            cursor.execute(query, (id_solicitud_prestamo,))
            fila = cursor.fetchone()
            cursor.close()
            return SolicitudPrestamoTablaDTO(*fila) if fila else None
        except Exception as e:
            print(f"Error al cargar la solicitud de préstamo con ID {id_solicitud_prestamo}: {e}")
            return None

    def buscar_solicitudes_prestamos(self, id_solicitud=None, id_empleado=None, id_tipo_estado_solicitud=None, fecha_inicio=None, fecha_fin=None) -> List[SolicitudPrestamoTablaDTO]:
        consulta = """
        SELECT 
            sp.id, 
            sp.id_empleado, 
            sp.monto, 
            tp.meses as periodo, 
            tp.interes, 
            sp.fecha_solicitud, 
            tes.nombre as estado
        FROM 
            SolicitudPrestamo sp
        JOIN 
            TipoPeriodo tp ON sp.id_tipo_periodo = tp.id
        JOIN
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        WHERE 1=1
        """
        parametros = []

        if id_solicitud:
            consulta += " AND sp.id = :1"
            parametros.append(id_solicitud)
        if id_empleado:
            consulta += " AND sp.id_empleado = :2"
            parametros.append(id_empleado)
        if id_tipo_estado_solicitud:
            consulta += " AND sp.id_tipo_estado_solicitud = :3"
            parametros.append(id_tipo_estado_solicitud)
        if fecha_inicio and fecha_fin:
            consulta += " AND sp.fecha_solicitud BETWEEN :4 AND :5"
            parametros.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            consulta += " AND sp.fecha_solicitud >= :4"
            parametros.append(fecha_inicio)
        elif fecha_fin:
            consulta += " AND sp.fecha_solicitud <= :4"
            parametros.append(fecha_fin)


        try:
            cursor = self.connection.cursor()
            cursor.execute(consulta, parametros)
            filas = cursor.fetchall()
            solicitudes_prestamos = [SolicitudPrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            return []

    def actualizar_estado_solicitud(self, id_solicitud_prestamo, id_nuevo_tipo_estado_solicitud):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE SolicitudPrestamo SET id_tipo_estado_solicitud = :1 WHERE id = :2", (id_nuevo_tipo_estado_solicitud, id_solicitud_prestamo))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            raise e

    def cancelar_solicitud_prestamo_por_id(self, id_solicitud_prestamo):
        try:
            cursor = self.connection.cursor()

            id_tipo_estado_cancelada = self.tipo_estado_solicitud_dao.obtener_id_tipo_estado_solicitud_por_nombre('CANCELADA')

            if id_tipo_estado_cancelada:
                # Actualizar la solicitud con el nuevo estado
                cursor.execute(
                    "UPDATE SolicitudPrestamo SET id_tipo_estado_solicitud = :1 WHERE id = :2",
                    (id_tipo_estado_cancelada, id_solicitud_prestamo)
                )
                self.connection.commit()
            else:
                raise ValueError("El estado 'CANCELADA' no existe en la tabla TipoEstadoSolicitud")

            cursor.close()

        except Exception as e:
            print(f"Error al cancelar la solicitud de préstamo: {e}")
            raise e