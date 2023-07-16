import json
from collections import Counter
from pprint import pprint
from typing import Dict, Union

import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

from ingredient_resolver import IngredientResolver, basic_materials, nauvis_materials
from prototype_parser import parse_prototypes
from recipe import Product, Ingredient, Recipe
from recipe_chooser import FirstRecipeChooser, MaxAmountChooser, CompositeRecipeChooser, OnlyProductChooser, \
    ProductIsFirstChooser, RecipenameMatchesProductChooser, DictionaryChooser
from recipe_finder import find_recipes_that_make_product
from recipe_parser import parse_recipes


def find_prototype_with_crafting_category(recipe, crafting_categories):
    for category, prototype in crafting_categories.items():
        if recipe.category == category:
            return max(crafting_categories[category], key=lambda x: x.crafting_speed)
    return None


class BuildingResolver:
    def __init__(self, crafting_categories):
        self.crafting_categories = crafting_categories

    def __call__(self, recipe: Recipe):
        return find_prototype_with_crafting_category(recipe, self.crafting_categories)


class RecipeResolver:
    def __init__(self, recipe_chooser, recipes):
        self.recipe_chooser = recipe_chooser
        self.recipes = recipes

    def __call__(self, product):
        recipes_that_produce_ingredient = find_recipes_that_make_product(str(product), recipes)
        print(len(recipes_that_produce_ingredient))
        chosen_recipe = recipe_chooser.choose_recipe(recipes_that_produce_ingredient, str(product))
        return chosen_recipe


if __name__ == '__main__':
    prototypes_path = "data/entity_prototypes.json"
    recipes_path = "data/recipes.json"
    # read both files and store result in variables
    with open(prototypes_path, "r") as f:
        prototypes = json.load(f)
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    crafting_categories = parse_prototypes(prototypes)
    recipes = parse_recipes(recipes)
    fixed_recipes = {'se-empty-data': 'se-empty-data'}
    recipe_chooser = CompositeRecipeChooser(
        [RecipenameMatchesProductChooser(), OnlyProductChooser(), FirstRecipeChooser()])
    for r in recipes:
        if r.name == "se-experimental-specimen":
            example = r
            break
    resolver = IngredientResolver(recipe_chooser, recipes)
    ingredient_recipes = resolver(example.products[0], example, 1)
    pprint({k: v for k, v in resolver.basket.items() if v != 0})
    recipe_resolver = RecipeResolver(recipe_chooser, recipes)
    building_resolver = BuildingResolver(crafting_categories)
    shopping_list = {(recipe_resolver(k), k): v for k, v in resolver.ingredient_basket.items()}
    order_list = {(building_resolver(r), r, k): v for (r, k), v in shopping_list.items()}
    mass_flow_rate = {(building, recipe, k): (v, (building.crafting_speed / recipe.energy) * recipe.average_amount(k))
                      for (building, recipe, k), v in order_list.items()}

    for (b, r, k), (v, flow) in mass_flow_rate.items():
        print(
            f"{b.name} makes {r.name} in {(v // flow) + 1} factories at {flow} per second, required flow is {v} per second")


    def recipe_to_ingredients_series(recipe: Recipe):
        inputs = pd.Series({i.name: i.amount for i in recipe.ingredients})
        outputs = pd.Series({p.name: p.average_amount for p in recipe.products})
        if None in inputs.index or None in outputs.index:
            print('?')
        if None in inputs.values or None in outputs.values:
            print('?')
        result = outputs.subtract(inputs, fill_value=0)
        result.name = recipe.name
        return result


    def building_and_recipe_to_CPM(building, recipe: Recipe):
        return building.crafting_speed / recipe.energy


    def optimize_transformations(df, production_rates, product, min_quantity):
        # Create a PuLP linear programming problem
        problem = LpProblem("Transformation Optimization", LpMinimize)

        # Define decision variables
        transformations = list(df.columns)
        items = df.index
        quantities = LpVariable.dicts("quantity", transformations, lowBound=0, cat="Continuous")
        penalties = LpVariable.dicts("penalty", items, lowBound=0, cat="Continuous")
        production_exprs = LpVariable.dicts("production_expr", items, cat="Continuous")
        penalty_coefficient = 100000
        # Define objective function
        penalty_terms = [penalty_coefficient * penalties[item] for item in items]
        objective_terms = [quantities[transformation] for transformation in transformations] + penalty_terms

        problem += lpSum(objective_terms)
        # Define constraints
        for item in df.index:

            production_exprs[item] = lpSum(
                [df.loc[item, transformation] * quantities[transformation] * production_rates.get(transformation,1) for
                 transformation in transformations])
            if item == product:
                problem += production_exprs[item] >= min_quantity
            else:
                if penalties.get(item) is not None:
                    problem += production_exprs[item] + penalties[item] >= 0

        # Solve the problem
        problem.solve()

        # Retrieve the results
        status = LpStatus[problem.status]
        optimal_quantities = {transformation: quantities[transformation].varValue for transformation in transformations}
        optimal_penalties = {item: penalties[item].varValue for item in items}
        return status, optimal_quantities, optimal_penalties, production_exprs


    free_resources = [
        Recipe(name=f'free {name}', ingredients=[], products=[Product(name=name, amount=1, type='free')], energy=1,
               category='free') for name in basic_materials]
    nauvis_resources = [
        Recipe(name=f'free {name}', ingredients=[], products=[Product(name=name, amount=1, type='nauvis')], energy=1,
               category='nauvis') for name in nauvis_materials]
    all_recipes= recipes + free_resources + nauvis_resources
    recipes_df = pd.DataFrame(
        [recipe_to_ingredients_series(r) for r in all_recipes]).fillna(0).T
    building_resolver = BuildingResolver(crafting_categories)
    production_rates = {recipe.name:building_resolver(recipe).crafting_speed / recipe.energy for recipe in all_recipes if building_resolver(recipe) is not None}
    status, optimal_quantities, penalties, production_exprs = optimize_transformations(recipes_df, production_rates,
                                                                                       'advanced-circuit', 1)
    # Print the results
    print("Status:", status)
    print("Optimal Quantities:")
    for transformation, quantity in optimal_quantities.items():
        if quantity != 0:
            print(transformation, ":", quantity)
    print("Penalties:")
    for item, penalty in penalties.items():
        if penalty != 0:
            print(item, ":", penalty)
    print("Production:")
    for item, expr in production_exprs.items():
        if expr.value() != 0:
            print(item, ":", expr.value())
