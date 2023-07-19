class ProductionLine:
    def __init__(self, status, optimal_quantities, production_exprs):
        self.status = status
        self.optimal_quantities = optimal_quantities
        self.production_exprs = production_exprs

    def print(self,epsilon=0.0001):
        print("Status:", self.status)
        print("Optimal Quantities:")
        for transformation, quantity in self.optimal_quantities.items():
            if quantity.value() > epsilon:
                print(transformation, ":", quantity.value())

        print("Production:")
        for item, expr in self.production_exprs.items():
            if expr.value() >epsilon:
                print(item, ":", expr.value())
