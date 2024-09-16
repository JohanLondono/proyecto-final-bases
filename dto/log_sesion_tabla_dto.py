class LogSesionTablaDTO:
    def __init__(self, id, id_usuario, nombre_empleado, apellido_empleado, id_empleado, fecha, tipo, estado):
        self.id = id  # ID del log de sesión
        self.id_usuario = id_usuario  # ID del usuario
        self.nombre_empleado = nombre_empleado  # Nombre del empleado
        self.apellido_empleado = apellido_empleado  # Apellido del empleado
        self.id_empleado = id_empleado  # ID del empleado
        self.fecha = fecha  # Fecha de la sesión
        self.tipo = tipo  # Tipo de sesión (ENTRADA/SALIDA)
        self.estado = estado  # Éxito de la sesión (EXITOSO/FALLIDO)

    def __repr__(self):
        return (f"LoginSesionTablaDTO(id={self.id}, id_usuario={self.id_usuario}, "
                f"nombre_empleado={self.nombre_empleado}, apellido_empleado={self.apellido_empleado}, "
                f"id_empleado={self.id_empleado}, fecha={self.fecha}, tipo={self.tipo}, estado={self.estado})")

    def __str__(self):
        return (f"LoginSesionTablaDTO({self.id}, {self.id_usuario}, {self.nombre_empleado}, "
                f"{self.apellido_empleado}, {self.id_empleado}, {self.fecha}, {self.tipo}, {self.estado})")