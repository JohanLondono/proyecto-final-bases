class SolicitudPrestamoTablaDTO:
    def __init__(self, id, id_empleado, monto, periodo, interes, fecha_solicitud, estado):
        self.id = id
        self.id_empleado = id_empleado
        self.monto = monto
        self.periodo = periodo
        self.interes = interes
        self.fecha_solicitud = fecha_solicitud
        self.estado = estado

    def __repr__(self):
        return (f"SolicitudPrestamoTablaDTO(id={self.id}, id_empleado={self.id_empleado}, "
                f"monto={self.monto}, periodo={self.periodo}, interes={self.interes}, "
                f"fecha_solicitud={self.fecha_solicitud}, estado={self.estado})")

    def __str__(self):
        return (f"SolicitudPrestamoTablaDTO({self.id}, {self.id_empleado}, {self.monto}, "
                f"{self.periodo}, {self.interes}, {self.fecha_solicitud}, {self.estado})")
