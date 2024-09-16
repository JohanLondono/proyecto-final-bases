class PrestamoDetalleDTO:
    def __init__(self, monto, interes, periodo, saldo_pendiente, estado_prestamo, fecha_aprobacion):
        self.monto = monto
        self.interes = interes
        self.periodo = periodo
        self.saldo_pendiente = saldo_pendiente
        self.estado_prestamo = estado_prestamo
        self.fecha_aprobacion = fecha_aprobacion

    def __repr__(self):
        return (f"PrestamoDetalleDTO(monto={self.monto}, interes={self.interes}, "
                f"periodo={self.periodo}, saldo_pendiente={self.saldo_pendiente}, "
                f"estado_prestamo={self.estado_prestamo}, fecha_aprobacion={self.fecha_aprobacion})")
    
    def __str__(self):
        return (f"PrestamoDetalleDTO({self.monto}, {self.interes}, {self.periodo}, "
                f"{self.saldo_pendiente}, {self.estado_prestamo}, {self.fecha_aprobacion}")