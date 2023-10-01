from typing import List, Tuple

from pulp import lpSum, LpVariable, LpProblem


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
    def __init__(self, products: [str], max_assemblers: int):
        self.products = products
        self.max_assemblers = max_assemblers

    def finalize(self, problem:LpProblem):
        # Make a little bit of everything at least
        for product in self.products:
            problem += problem.net_production[product] >= 0
        # New Variables: Integer variables for the number of assemblers
        problem.int_building_count = LpVariable.dicts(
            "int_building_count", problem.recipes, lowBound=0, cat="Integer"
        )
        # Make the new variables greater than their corresponding building_count variables
        for recipe in problem.recipes:
            problem += problem.int_building_count[recipe] >= problem.building_count[recipe]
        # Constraint: limit number of non-ltn assemblers
        problem += lpSum(value for key,value in problem.int_building_count.items() if not 'ltn' in key) <= self.max_assemblers
        # Objective: maximize production of products
        objective_terms = [problem.net_production[product] for product in self.products]
        problem += lpSum(objective_terms)
        problem.sense=-1
        return problem
