class SucursalTablaDTO:
    def __init__(self, codigo, nombre, departamento, municipio, presupuesto):
        self.codigo = codigo
        self.nombre = nombre
        self.departamento = departamento
        self.municipio = municipio
        self.presupuesto = presupuesto

    def __repr__(self):
        return (f"SucursalTablaDTO(codigo={self.codigo}, nombre={self.nombre}, "
                f"departamento={self.departamento}, municipio={self.municipio}, "
                f"presupuesto={self.presupuesto})")

    def __str__(self):
        return (f"SucursalTablaDTO({self.nombre}, {self.municipio}, "
                f"{self.presupuesto})")