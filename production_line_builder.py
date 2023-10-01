from typing import List, Tuple

import numpy as np
import pandas as pd
import pulp

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

from production_line import ProductionLine
from production_site import ProductionSite
from recipe_provider import RecipeProvider


class ProductionLineBuilder:
    def __init__(self, recipe_provider, building_resolver):
        self.recipe_provider: RecipeProvider = recipe_provider
        self.building_resolver = building_resolver
        self.production_rates = {
            recipe.name: self.building_resolver(recipe).crafting_speed / recipe.energy
            for recipe in self.recipe_provider.recipes
            if self.building_resolver(recipe)
               is not None  # Free recipes are not craftable
        }

    def build(self, product_quantity: List[Tuple[str, float]]):
        recipes_df = self.recipe_provider.as_dataframe()
        status, production_sites, production_exprs = optimize_transformations(
            recipes_df, self.production_rates, product_quantity
        )
        epsilon = 0.0001
        production_sites = {
            k: ProductionSite(
                recipe=self.recipe_provider.by_name(k),
                quantity=v.value(),
                building=self.building_resolver(self.recipe_provider.by_name(k)),
            )
            for k, v in production_sites.items()
            if (v.value() or 0) > epsilon
        }
        net_production = {
            k: v.value()
            for k, v in production_exprs.items()
            if (v.value() or 0) > epsilon
        }
        return ProductionLine(status, production_sites, net_production)


def optimize_transformations(recipe_df, production_rates, product_min_quantity):
    problem = LpProblem("ProductionLineProblem", LpMinimize)
    recipes = list(recipe_df.columns)
    building_count = LpVariable.dicts(
        "building_count", recipe_df.columns, lowBound=0, cat="Continuous"
    )
    net_production = LpVariable.dicts(
        "net_production", recipe_df.index, lowBound=0, cat="Continuous"
    )

    # Define constraints
    recipe_dict = recipe_df.to_dict()
    for item in recipe_df.index:
        p = lpSum(
            [
                recipe_dict[transformation][item]
                * building_count[transformation]
                * production_rates.get(transformation, 1)
                for transformation in recipes
            ]
        )
        problem += net_production[item] == p

    # Make the required quantity of product
    for product, min_quantity in product_min_quantity:
        problem += net_production[product] >= min_quantity

    # Forbid production of trash
    for item in {"se-broken-data", "se-contaminated-scrap"}:
        problem += net_production[item] == 0

    # Objective: Minimize excess production (free recipes are not part of the objective)
    objective_terms = [building_count[transformation] for transformation in recipes if not transformation.startswith("ltn")]
    problem += lpSum(objective_terms)

    problem.solve()
    status = LpStatus[problem.status]
    return status, building_count, net_production
