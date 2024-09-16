class EmpleadoDTO:
    def __init__(self, id_empleado: int, nombre: str, apellido: str, sucursal_codigo: int, puesto: str, salario: float):
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.apellido = apellido
        self.sucursal_codigo = sucursal_codigo
        self.puesto = puesto
        self.salario = salario

    def __repr__(self):
        return f"EmpleadoDTO(id_empleado={self.id_empleado}, nombre={self.nombre}, apellido={self.apellido}, sucursal_codigo={self.sucursal_codigo}, puesto={self.puesto}, salario={self.salario})"

    def __str__(self):
        return f"EmpleadoDTO({self.nombre}, {self.apellido}, {self.puesto}, {self.salario})"