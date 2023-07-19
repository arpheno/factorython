from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

from production_line import ProductionLine


class ProductionLineBuilder:
    def __init__(self, recipe_provider, building_resolver):
        self.recipe_provider = recipe_provider
        self.building_resolver = building_resolver

    def build(self, product, quantity):
        recipes_df = self.recipe_provider.as_dataframe()
        production_rates = {
            recipe.name: self.building_resolver(recipe).crafting_speed / recipe.energy
            for recipe in self.recipe_provider.recipes
            if self.building_resolver(recipe)
            is not None  # Some recipes are not craftable?
        }
        status, optimal_quantities, production_exprs = optimize_transformations(
            recipes_df, production_rates, [(product, quantity)]
        )
        return ProductionLine(status, optimal_quantities, production_exprs)


def optimize_transformations(recipe_df, production_rates, product_min_quantity):
    problem = LpProblem("Production Line Problem", LpMinimize)
    recipes = list(recipe_df.columns)
    building_count = LpVariable.dicts(
        "building_count", recipe_df.columns, lowBound=0, cat="Continuous"
    )
    net_production = LpVariable.dicts(
        "net_production", recipe_df.index, lowBound=0, cat="Continuous"
    )

    # Define constraints
    for item in recipe_df.index:
        p = lpSum(
            [
                recipe_df.loc[item, transformation]
                * building_count[transformation]
                * production_rates.get(transformation, 1)
                for transformation in recipes
            ]
        )
        problem += net_production[item] == p

    # Make the required quantity of product
    for product,min_quantity in product_min_quantity:
        problem += net_production[product] >= min_quantity

    # Forbid production of trash
    for item in {"se-broken-data", "se-contaminated-scrap"}:
        problem += net_production[item] == 0

    # Objective: Minimize excess production
    objective_terms = [building_count[transformation] for transformation in recipes]
    problem += lpSum(objective_terms)

    problem.solve()

    status = LpStatus[problem.status]
    return status, building_count, net_production
