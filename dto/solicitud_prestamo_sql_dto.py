class SolicitudPrestamoSqlDTO:
    def __init__(self, id, id_empleado, monto, id_tipo_periodo, fecha_solicitud, id_tipo_estado_solicitud):
        self.id = id
        self.id_empleado = id_empleado
        self.monto = monto
        self.id_tipo_periodo = id_tipo_periodo
        self.fecha_solicitud = fecha_solicitud
        self.id_tipo_estado_solicitud = id_tipo_estado_solicitud

    def __repr__(self):
        return (f"SolicitudPrestamoSqlDTO(id={self.id}, id_empleado={self.id_empleado}, "
                f"monto={self.monto}, id_tipo_periodo={self.id_tipo_periodo}, "
                f"fecha_solicitud={self.fecha_solicitud}, id_tipo_estado_solicitud={self.id_tipo_estado_solicitud})")

    def __str__(self):
        return (f"SolicitudPrestamoSqlDTO({self.id}, {self.id_empleado}, {self.monto}, "
                f"{self.id_tipo_periodo}, {self.fecha_solicitud}, {self.id_tipo_estado_solicitud})")
