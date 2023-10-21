from typing import List, Tuple

from pulp import lpSum, LpVariable, LpProblem


class ModelSpecialization:
    def finalize(self, problem):
        pass


class CoreHelmodModel(LpProblem):
    def __init__(self, *args, **kwargs):
        super(CoreHelmodModel, self).__init__(*args, **kwargs)
        self.net_production = None
        self.building_count = None
        self.recipes = None


class ProductionLineProblem(ModelSpecialization):
    def __init__(self, product_min_quantity: List[Tuple[str, float]]):
        self.product_min_quantity = product_min_quantity

    def finalize(self, problem: CoreHelmodModel):
        # Make the required quantity of product
        for product, min_quantity in self.product_min_quantity:
            problem += problem.net_production[product] >= min_quantity

        # Forbid production of trash
        for item in {"se-broken-data", "se-contaminated-scrap"}:
            problem += problem.net_production[item] == 0

        # Objective: Minimize building count (free recipes are not part of the objective)
        objective_terms = [problem.building_count[transformation] for transformation in problem.recipes if
                           not transformation.startswith("ltn")]
        problem += lpSum(objective_terms)
        return problem


class CargoWagonProblem(ModelSpecialization):
    def __init__(self, products: [str], max_assemblers: int):
        self.products = products
        self.max_assemblers = max_assemblers

    def finalize(self, problem: CoreHelmodModel):
        # New Variables: Integer variables for the number of assemblers
        problem.int_building_count = LpVariable.dicts(
            "int_building_count", problem.recipes, lowBound=0, cat="Integer"
        )
        # Make the new variables greater than their corresponding building_count variables
        for recipe in problem.recipes:
            problem += problem.int_building_count[recipe] >= problem.building_count[recipe]
        # Constraint: limit number of non-ltn assemblers
        problem += lpSum(
            value for key, value in problem.int_building_count.items() if not 'ltn' in key) <= self.max_assemblers
        # Objective: maximize production of products
        objective_terms = [problem.net_production[product] for product in self.products]
        problem += lpSum(objective_terms)
        problem.sense = -1
        return problem


class CargoWagonMallProblem(ModelSpecialization):
    def __init__(self, products: [(float, str)], max_assemblers: int):
        self.products = products
        self.max_assemblers = max_assemblers

    def finalize(self, problem: CoreHelmodModel):
        # New Variables: Integer variables for the number of assemblers
        problem.int_building_count = LpVariable.dicts(
            "int_building_count", problem.recipes, lowBound=0, cat="Integer"
        )
        # Make the new variables greater than their corresponding building_count variables
        for recipe in problem.recipes:
            problem += problem.int_building_count[recipe] >= problem.building_count[recipe]
        # Constraint: limit number of non-ltn assemblers
        problem += lpSum(
            value for key, value in problem.int_building_count.items() if not 'ltn' in key) <= self.max_assemblers
        # Create variable for each term of the objective

        weighted_product_quantities = LpVariable.dicts(
            "weighted_product_quantities", [product for factor, product in self.products],
            lowBound=0, cat="Continuous"
        )
        minimum_weighted_product_quantity = LpVariable('minimum_weighted_product_quantity')
        for (factor, product) in self.products:
            problem += weighted_product_quantities[product] == (1/factor) * problem.net_production[product]
            problem += minimum_weighted_product_quantity <= weighted_product_quantities[product]
        objective_terms = [minimum_weighted_product_quantity]
        problem += lpSum(objective_terms)
        problem.sense = -1
        return problem
