class EmpleadoSqlDTO:
    def __init__(self, id_empleado: int, nombre: str, apellido: str, sucursal_codigo: int, id_tipo_cargo):
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.apellido = apellido
        self.sucursal_codigo = sucursal_codigo
        self.id_tipo_cargo = id_tipo_cargo

    def __repr__(self):
        return f"EmpleadoSqlDTO(id_empleado={self.id_empleado}, nombre={self.nombre}, apellido={self.apellido}, sucursal_codigo={self.sucursal_codigo}, id_tipo_cargo={self.id_tipo_cargo})"

    def __str__(self):
        return f"EmpleadoSqlDTO({self.id_empleado}, {self.nombre}, {self.apellido}, {self.id_tipo_cargo})"