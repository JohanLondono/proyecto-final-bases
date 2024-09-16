class UsuarioDTO:
    def __init__(self, id_empleado, nombre_usuario, email, contraseña, rol):
        self.id_empleado = id_empleado
        self.nombre_usuario = nombre_usuario
        self.email = email
        self.contraseña = contraseña
        self.rol = rol

    def __repr__(self):
        return (f"UsuarioDTO(id_empleado={self.id_empleado}, nombre_usuario={self.nombre_usuario}, "
                f"email={self.email}, contraseña={self.contraseña}, "
                f"rol={self.rol})")

    def __str__(self):
        return (f"UsuarioDTO({self.id_empleado}, {self.nombre_usuario}, "
                f"{self.email}, {self.contraseña}, {self.rol})")