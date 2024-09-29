class UsuarioSqlDTO:
    def __init__(self, id_empleado, nombre_usuario, email, contraseña, id_tipo_usuario):
        self.id_empleado = id_empleado
        self.nombre_usuario = nombre_usuario
        self.email = email
        self.contraseña = contraseña
        self.id_tipo_usuario = id_tipo_usuario

    def __repr__(self):
        return (f"UsuarioSqlDTO(id_empleado={self.id_empleado}, nombre_usuario={self.nombre_usuario}, "
                f"email={self.email}, contraseña={self.contraseña}, "
                f"id_tipo_usuario={self.id_tipo_usuario})")

    def __str__(self):
        return (f"UsuarioSqlDTO({self.id_empleado}, {self.nombre_usuario}, "
                f"{self.email}, {self.contraseña}, {self.id_tipo_usuario})")