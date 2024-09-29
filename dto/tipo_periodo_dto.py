class TipoPeriodoDTO:
    def __init__(self, id, meses, interes):
        self.id = id
        self.meses = meses
        self.interes = interes

    def __repr__(self):
        return (f"TipoPeriodoDTO(id={self.id}, meses={self.meses}, "
                f"interes={self.interes})")

    def __str__(self):
        return (f"TipoPeriodoDTO({self.id}, {self.meses}, "
                f"{self.interes})")