from dto import PrestamoSqlDTO
from dto import PrestamoTablaDTO
from dto import PrestamoDetalleDTO
from .tipo_estado_prestamo_dao import TipoEstadoPrestamoDAO

from typing import List

class PrestamoDAO:
    def __init__(self, connection):
        self.connection = connection
        self.tipo_estado_prestamo_dao = TipoEstadoPrestamoDAO(self.connection)

    def cargar_todos_los_prestamos(self) -> List[PrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                p.id AS id_prestamo,
                p.id_solicitud,
                sp.id_empleado,
                MAX(pg.fecha_pago) AS fecha_ult_pago,
                p.saldo_pendiente,
                COALESCE(SUM(pg.monto_pagado), 0) AS saldo_acumulado,
                COUNT(pg.id) AS numero_pagos,
                p.fecha_aprobacion,
                p.fecha_vencimiento,
                tep.nombre as estado_prestamo
            FROM 
                Prestamo p
            JOIN 
                TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id
            JOIN 
                SolicitudPrestamo sp ON p.id_solicitud = sp.id
            LEFT JOIN 
                Pago pg ON pg.id_prestamo = p.id
            GROUP BY 
                p.id, p.id_solicitud, sp.id_empleado, p.saldo_pendiente, p.fecha_aprobacion, p.fecha_vencimiento, tep.nombre
            ORDER BY p.id
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            solicitudes_prestamos = [PrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(e)
            return []
    
    def cargar_prestamos_por_empleado(self, id_empleado) -> List[PrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                p.id AS id_prestamo,
                p.id_solicitud,
                sp.id_empleado,
                MAX(pg.fecha_pago) AS fecha_ult_pago,
                p.saldo_pendiente,
                COALESCE(SUM(pg.monto_pagado), 0) AS saldo_acumulado,
                COUNT(pg.id) AS numero_pagos,
                p.fecha_aprobacion,
                p.fecha_vencimiento,
                tep.nombre as estado_prestamo
            FROM 
                Prestamo p
            JOIN 
                TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id
            JOIN 
                SolicitudPrestamo sp ON p.id_solicitud = sp.id
            LEFT JOIN 
                Pago pg ON pg.id_prestamo = p.id
            WHERE 
                sp.id_empleado = :id_empleado
            GROUP BY 
                p.id, p.id_solicitud, sp.id_empleado, p.saldo_pendiente, p.fecha_aprobacion, p.fecha_vencimiento, tep.nombre
            ORDER BY 
                p.id
            """
            cursor.execute(query, {"id_empleado": id_empleado})
            filas = cursor.fetchall()
            solicitudes_prestamos = [PrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(e)
            return []
    
    def obtener_datos_solicitud_prestamo_por_id_prestamo(self, id_prestamo) -> PrestamoDetalleDTO:
        try:
            cursor = self.connection.cursor()
            # Consultar los datos del préstamo
            query = """
            SELECT 
                s.monto, 
                tp.interes, 
                tp.meses as periodo, 
                p.saldo_pendiente, 
                tep.nombre as estado_prestamo, 
                p.fecha_aprobacion 
            FROM 
                SolicitudPrestamo s 
            JOIN 
                TipoPeriodo tp ON s.id_tipo_periodo = tp.id
            JOIN 
                Prestamo p ON s.id = p.id_solicitud 
            JOIN 
                TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id
            WHERE 
                p.id = :id_prestamo
            """
            cursor.execute(query, {'id_prestamo': id_prestamo})
            fila = cursor.fetchone()
            cursor.close()
            return PrestamoDetalleDTO(*fila) if fila else None

        except Exception as e:
            print(e)

    def obtener_saldo_y_estado_prestamo(self, id_prestamo):
        cursor = self.connection.cursor()
        try:
            query = """
            SELECT 
                p.saldo_pendiente, 
                tep.nombre as estado_prestamo 
            FROM 
                Prestamo p
            JOIN 
                TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id
            WHERE 
                p.id = :id_prestamo
            """
            cursor.execute(query, {'id_prestamo': id_prestamo})
            prestamo = cursor.fetchone()
            return prestamo  # Devuelve (saldo_pendiente, estado_prestamo) o None si no se encuentra.
        except Exception as e:
            print(f"Error al obtener saldo y estado del préstamo: {str(e)}")
            return None
        finally:
            cursor.close()

    def actualizar_saldo_y_estado_prestamo(self, id_prestamo, saldo_pendiente, id_nuevo_tipo_estado_prestamo):
        cursor = self.connection.cursor()
        try:
            query = """
                UPDATE Prestamo 
                SET saldo_pendiente = :saldo_pendiente, id_tipo_estado_prestamo = :id_nuevo_tipo_estado_prestamo
                WHERE id = :id_prestamo
            """
            cursor.execute(query, {
                'saldo_pendiente': saldo_pendiente,
                'id_nuevo_tipo_estado_prestamo': id_nuevo_tipo_estado_prestamo,
                'id_prestamo': id_prestamo
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar saldo y estado del préstamo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()


    def insertar_prestamo(self, prestamo: PrestamoSqlDTO):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Prestamo (id_solicitud, fecha_aprobacion, fecha_vencimiento, saldo_pendiente, id_tipo_estado_prestamo)
                VALUES (:1, :2, :3, :4, :5)
            """, (prestamo.id_solicitud, prestamo.fecha_aprobacion, prestamo.fecha_vencimiento, prestamo.saldo_pendiente, prestamo.id_tipo_estado_prestamo))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            cursor.close()

    def cancelar_prestamo_por_id_solicitud(self, id_solicitud_prestamo):
        try:
            cursor = self.connection.cursor()

            id_tipo_estado_cancelada = self.tipo_estado_prestamo_dao.obtener_id_tipo_estado_prestamo_por_nombre('CANCELADO')

            if id_tipo_estado_cancelada:
                # Actualizar la solicitud con el nuevo estado
                cursor.execute(
                    "UPDATE Prestamo SET id_tipo_estado_prestamo = :1 WHERE id_solicitud = :2",
                    (id_tipo_estado_cancelada, id_solicitud_prestamo)
                )
                self.connection.commit()
            else:
                raise ValueError("El estado 'CANCELADO' no existe en la tabla TipoEstadoPrestamo")

            cursor.close()
        except Exception as e:
            raise e

    def buscar_prestamos(self, id_prestamo=None, id_solicitud=None, id_empleado=None, id_tipo_estado_prestamo=None) -> List[PrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            
            # Crear una consulta SQL dinámica
            query = """
            SELECT 
                p.id AS id_prestamo,
                p.id_solicitud,
                sp.id_empleado,
                MAX(pg.fecha_pago) AS fecha_ult_pago,
                p.saldo_pendiente,
                COALESCE(SUM(pg.monto_pagado), 0) AS saldo_acumulado,
                COUNT(pg.id) AS numero_pagos,
                p.fecha_aprobacion,
                p.fecha_vencimiento,
                tep.nombre as estado_prestamo
            FROM 
                Prestamo p
            JOIN 
                TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id
            JOIN 
                SolicitudPrestamo sp ON p.id_solicitud = sp.id
            LEFT JOIN 
                Pago pg ON pg.id_prestamo = p.id
            WHERE 1=1
            """
            
            # Agregar condiciones basadas en los filtros de búsqueda
            params = []
            if id_prestamo:
                query += " AND p.id = :1"
                params.append(id_prestamo)
            if id_solicitud:
                query += " AND p.id_solicitud = :2"
                params.append(id_solicitud)
            if id_empleado:
                query += " AND sp.id_empleado = :3"
                params.append(id_empleado)
            if id_tipo_estado_prestamo:
                query += " AND p.id_tipo_estado_prestamo = :4"
                params.append(id_tipo_estado_prestamo)

            query += """
            GROUP BY 
                p.id, p.id_solicitud, sp.id_empleado, p.saldo_pendiente, p.fecha_aprobacion, p.fecha_vencimiento, tep.nombre
            ORDER BY p.id
            """
            cursor.execute(query, params)
            filas = cursor.fetchall()
            prestamos = [PrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return prestamos
        except Exception as e:
            print(e)
            return []