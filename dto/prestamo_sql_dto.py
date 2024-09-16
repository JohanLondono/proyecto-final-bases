class PrestamoSqlDTO:
    def __init__(self, id, id_solicitud, fecha_aprobacion, fecha_vencimiento, saldo_pendiente, estado_prestamo):
        self.id = id
        self.id_solicitud = id_solicitud
        self.fecha_aprobacion = fecha_aprobacion
        self.fecha_vencimiento = fecha_vencimiento
        self.saldo_pendiente = saldo_pendiente
        self.estado_prestamo = estado_prestamo

    def __repr__(self):
        return (f"PrestamoSqlDTO(id={self.id}, id_solicitud={self.id_solicitud}, fecha_aprobacion={self.fecha_aprobacion}, "
                f"fecha_vencimiento={self.fecha_vencimiento}, saldo_pendiente={self.saldo_pendiente}, "
                f"estado_prestamo={self.estado_prestamo})")

    def __str__(self):
        return (f"PrestamoSqlDTO({self.id}, {self.id_solicitud}, {self.fecha_aprobacion}, "
                f"{self.fecha_vencimiento}, {self.saldo_pendiente}, {self.estado_prestamo})")