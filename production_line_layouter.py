from typing import List, Tuple

import numpy as np
import pandas as pd
import pulp

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

from production_line import ProductionLine
from production_site import ProductionSite
from recipe_provider import RecipeProvider


class ProductionLineLayouter:
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

    def heuristic_arrangement(self, production_line: ProductionLine):
        flows = []
        for recipe_name, site in production_line.production_sites.items():
            flow = pd.Series({
                **{
                    product.name: product.average_amount
                    for product in site.recipe.products
                },
                **{
                    ingredient.name: -ingredient.amount
                    for ingredient in site.recipe.ingredients
                }
            }
            ) * self.production_rates.get(recipe_name, 1)
            num_copies = site.building_count
            df = pd.concat([flow] * num_copies, axis=1)
            df.columns = [f"{site.recipe.name}_{i}" for i in range(1, num_copies + 1)]
            flows.append(df)
        merged_df = pd.concat(flows, axis=1).fillna(0)
        print(merged_df)
        group_count = merged_df.columns // 20 + 1

        return merged_df

    def organize(self, production_line: ProductionLine):
        ingredient_flows = []
        production_flows = []

        for recipe_name, site in production_line.production_sites.items():
            ingredient_flow = pd.Series(
                {
                    ingredient.name: ingredient.amount
                    for ingredient in site.recipe.ingredients
                }
            ) * self.production_rates.get(recipe_name, 1)
            fractional_flows = [1 if x < site.quantity - 1 else site.quantity % 1 for x in range(site.building_count)]
            df = pd.concat([ingredient_flow] * site.building_count, axis=1) * fractional_flows
            df.columns = [f"{site.recipe.name}_{i}" for i in range(1, site.building_count + 1)]
            ingredient_flows.append(df)
            production_flow = pd.Series(
                {product.name: product.amount for product in site.recipe.products}
            )
            production_flow *= self.production_rates.get(recipe_name, 1)
            df = pd.concat([production_flow] * site.building_count, axis=1) * fractional_flows
            df.columns = [f"{site.recipe.name}_{i}" for i in range(1, site.building_count + 1)]
            production_flows.append(df)

        ingredient_flows = pd.concat(ingredient_flows, axis=1)
        production_flows = pd.concat(production_flows, axis=1)
        missing_rows_in_ingredients = list(set(production_flows.index) - set(ingredient_flows.index))
        missing_rows_in_production = list(set(ingredient_flows.index) - set(production_flows.index))
        # add a row of zeros for missing ingredients
        ingredient_flows = pd.concat(
            [ingredient_flows, pd.DataFrame(0, index=missing_rows_in_ingredients, columns=ingredient_flows.columns)],
            axis=0)
        # if some product is missing, we need a new column in the production_flows, that produces 1 of that product
        ingredient_flows = pd.concat(
            [ingredient_flows, pd.DataFrame(0, index=production_flows.index, columns=missing_rows_in_production)],
            axis=1)
        # extend the index of the production_flows with the missing ingredients
        production_flows = pd.concat(
            [production_flows, pd.DataFrame(0, index=missing_rows_in_production, columns=production_flows.columns)],
            axis=0)
        # if some product is missing, we need a new column in the production_flows, that produces 1 of that product
        production_flows = pd.concat(
            [production_flows, pd.DataFrame(0, index=production_flows.index, columns=missing_rows_in_production)],
            axis=1)
        # make a new
        production_flows.loc[missing_rows_in_production, missing_rows_in_production] = np.eye(
            len(missing_rows_in_production))
        ingredient_flows.loc[missing_rows_in_ingredients, missing_rows_in_ingredients] = np.eye(
            len(missing_rows_in_ingredients))
        missing_columns_in_ingredients = list(set(production_flows.columns) - set(ingredient_flows.columns))
        missing_columns_in_production = list(set(ingredient_flows.columns) - set(production_flows.columns))

        ingredient_flows = ingredient_flows.sort_index().fillna(0)
        production_flows = production_flows.sort_index().fillna(0)
        # ensure the same order of columns
        ingredient_flows = ingredient_flows[production_flows.columns]

        print(f'ingredient_flows = np.{repr(ingredient_flows.values)}')
        print(f'product_flows = np.{repr(production_flows.values)}')
        connections = create_factory_connections(ingredient_flows.values, production_flows.values)
        # restore the dataframe from the connection matrix
        connections = pd.DataFrame(connections, index=ingredient_flows.columns, columns=production_flows.columns)
        return connections


def create_factory_connections(ingredient_flows, product_flows):
    items, sites = ingredient_flows.shape
    model = pulp.LpProblem("Factory_Connections", pulp.LpMinimize)

    connections = pulp.LpVariable.dicts(
        "Connection", (range(sites), range(sites)), cat="continuous", upBound=1, lowBound=0,
    )

    # Constraints: Each site should have all the ingredients it needs
    print('creating constraints')
    for site in range(sites):
        for ingredient in range(items):
            total_inflow = pulp.lpSum(
                product_flows[ingredient][other_site] * connections[other_site][site]
                for other_site in range(sites)
            )
            constraint = total_inflow >= ingredient_flows[ingredient][site]
            model += constraint
    model += pulp.lpSum(connections)
    print('solving')
    model.solve()
    print('done solving')
    print(model.status)

    connections_matrix = np.zeros((sites, sites))
    for site1 in range(sites):
        for site2 in range(sites):
            connections_matrix[site1][site2] = pulp.value(connections[site1][site2])

    return connections_matrix


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

    # Objective: Minimize excess production
    objective_terms = [building_count[transformation] for transformation in recipes]
    problem += lpSum(objective_terms)

    problem.solve()
    status = LpStatus[problem.status]
    return status, building_count, net_production
