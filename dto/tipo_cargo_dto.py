class TipoCargoDTO:
    def __init__(self, id, nombre, salario, tope_salario):
        self.id = id
        self.nombre = nombre
        self.salario = salario
        self.tope_salario = tope_salario

    def __repr__(self):
        return (f"TipoCargoDTO(id={self.id}, nombre={self.nombre}, "
                f"salario={self.salario}, tope_salario={self.tope_salario})")

    def __str__(self):
        return (f"TipoCargoDTO({self.id}, {self.nombre}, "
                f"{self.salario}, {self.tope_salario})")