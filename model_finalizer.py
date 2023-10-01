from typing import List, Tuple

from pulp import lpSum


class ModelSpecialization:
    def finalize(self, problem):
        pass


class ProductionLineProblem(ModelSpecialization):
    def __init__(self, product_min_quantity: List[Tuple[str, float]]):
        self.product_min_quantity = product_min_quantity

    def finalize(self, problem):
        # Make the required quantity of product
        for product, min_quantity in self.product_min_quantity:
            problem += problem.net_production[product] >= min_quantity

        # Forbid production of trash
        for item in {"se-broken-data", "se-contaminated-scrap"}:
            problem += problem.net_production[item] == 0

        # Objective: Minimize excess production (free recipes are not part of the objective)
        objective_terms = [problem.building_count[transformation] for transformation in problem.recipes if
                           not transformation.startswith("ltn")]
        problem += lpSum(objective_terms)
        return problem
class CargoWagonProblem(ModelSpecialization):
    def __init__(self, products: [str],max_assemblers: int):
        self.products=products
        self.max_assemblers=max_assemblers

    def finalize(self, problem):
        # Make the required quantity of product
        for product, min_quantity in self.product_min_quantity:
            problem += problem.net_production[product] >= min_quantity

        # Objective: Minimize excess production (free recipes are not part of the objective)
        objective_terms = [problem.building_count[transformation] for transformation in problem.recipes if
                           not transformation.startswith("ltn")]
        problem += lpSum(objective_terms)
        return problem
