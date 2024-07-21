import json
from functools import cached_property
import pulp
from collections import defaultdict

from draftsman.prototypes.assembling_machine import AssemblingMachine

from builders.building_resolver import build_building_resolver
from builders.recipe_transformations import build_recipe_transformations
from config.schemas.mall_maker_schema import MallMakerConfig
from model_finalizer import CargoWagonMallProblem
from production_line import ProductionLine
from production_line_builder import ProductionLineBuilder
from recipe_provider_builder import (
    build_recipe_provider,
    apply_transformers,
)

import yaml

AssemblingMachine


class MallMaker:
    def __init__(self, config: MallMakerConfig):
        self.config = config

        self.target_products = self.config.target_products
        self.max_assemblers = self.config.max_assemblers

        assembly = json.load(open(self.config.assembly_path))

        self.building_resolver = build_building_resolver(
            assembly, self.config.building_resolver_overrides
        )

        recipes = json.load(open(self.config.recipe_path))
        self._recipe_provider = build_recipe_provider(recipes, self.building_resolver)
        self._recipe_transformations = build_recipe_transformations(
            self.config, self.building_resolver
        )

    @cached_property
    def recipe_provider(self):
        result = apply_transformers(
            self._recipe_provider, self._recipe_transformations
        )
        return result

    def validate_self(self):
        for _, target_product in self.target_products:
            self.validate(target_product)

    def validate(self, product):
        try:
            self._recipe_provider.by_name(product)
        except ValueError:
            raise ValueError(f"Recipe {product} not found")

    def make_mall(self):
        self.target_products= [(15,'se-vulcanite-block')]
        for _, target_product in self.target_products:
            self.validate(target_product)
        lines: ProductionLine = [
            (target_product, self.build_optimal_ratios([target_product]))
            for target_product in self.target_products
        ]
        line=lines[0][1]
        line.print()
        stuff_to_be_made = [
            {
                "name": target[1],
                "required_recipes": {
                    recipe: site.quantity
                    for recipe, site in line.production_sites.items()
                },
            }
            for target, line in lines
        ]
        # print(stuff_to_be_made)
        # self.group_lines(1)

    def group_lines(self, stuff_to_be_made):
        # Example input data
        stuff_to_be_made = [
            {
                "name": "assembling-machine-3",
                "required_recipes": {
                    "advanced-circuit": 6.0,
                    "assembling-machine-1": 0.0625,
                    "assembling-machine-2": 0.0625,
                    "assembling-machine-3": 0.0625,
                    "burner-assembling-machine": 0.0625,
                    "concrete": 1.0,
                    "copper-cable": 7.0,
                    "electric-engine-unit": 5.0,
                    "electric-motor": 1.1,
                    "iron-gear-wheel": 1.0,
                    "iron-stick": 0.05,
                    "motor": 0.075,
                    "stone-tablet": 1.0,
                    "electronic-circuit-stone": 2.625,
                    "ltn water": 10.0,
                    "ltn iron-plate": 6.6,
                    "ltn copper-plate": 14.0,
                    "ltn stone-brick": 3.0,
                    "ltn steel-plate": 2.25,
                    "ltn sand": 1.0,
                    "ltn lubricant": 20.0,
                    "ltn plastic-bar": 2.0,
                },
            },
            {
                "name": "industrial-furnace",
                "required_recipes": {
                    "advanced-circuit": 5.0,
                    "concrete": 1.0,
                    "copper-cable": 5.9294872,
                    "electric-furnace": 0.32051282,
                    "industrial-furnace": 0.44871795,
                    "iron-stick": 0.05,
                    "processing-unit": 2.5641026,
                    "se-heat-shielding": 4.0,
                    "steel-furnace": 0.25,
                    "stone-furnace": 0.041666667,
                    "stone-tablet": 2.0,
                    "sulfur": 1.6,
                    "electronic-circuit-stone": 3.3974359,
                    "ltn water": 58.0,
                    "ltn stone": 0.41666667,
                    "ltn iron-plate": 0.1,
                    "ltn copper-plate": 11.858974,
                    "ltn stone-brick": 5.0,
                    "ltn steel-plate": 2.6461538,
                    "ltn sand": 1.0,
                    "ltn sulfuric-acid": 1.2820513,
                    "ltn petroleum-gas": 48.0,
                    "ltn plastic-bar": 1.6666667,
                },
            },
            {
                "name": "fast-transport-belt",
                "required_recipes": {
                    "fast-transport-belt": 4.0,
                    "iron-gear-wheel": 22.0,
                    "motor": 2.4,
                    "transport-belt": 2.0,
                    "ltn iron-plate": 96.0,
                },
            },
            {
                "name": "fast-inserter",
                "required_recipes": {
                    "burner-inserter": 1.6666667,
                    "copper-cable": 10.0,
                    "electric-motor": 2.6666667,
                    "fast-inserter": 1.6666667,
                    "inserter": 1.6666667,
                    "iron-gear-wheel": 4.0,
                    "iron-stick": 1.6666667,
                    "motor": 2.0,
                    "stone-tablet": 0.83333333,
                    "electronic-circuit-stone": 3.3333333,
                    "ltn iron-plate": 32.666667,
                    "ltn copper-plate": 20.0,
                    "ltn stone-brick": 1.6666667,
                },
            },
            {
                "name": "stack-filter-inserter",
                "required_recipes": {
                    "advanced-circuit": 2.6341463,
                    "burner-inserter": 0.2195122,
                    "copper-cable": 9.0,
                    "electric-motor": 0.35121951,
                    "fast-inserter": 0.2195122,
                    "inserter": 0.2195122,
                    "iron-gear-wheel": 4.0,
                    "iron-stick": 0.2195122,
                    "motor": 0.26341463,
                    "stack-filter-inserter": 0.2195122,
                    "stack-inserter": 0.2195122,
                    "stone-tablet": 1.3170732,
                    "electronic-circuit-stone": 5.2682927,
                    "ltn iron-plate": 18.195122,
                    "ltn copper-plate": 18.0,
                    "ltn stone-brick": 2.6341463,
                    "ltn plastic-bar": 0.87804878,
                },
            },
            {
                "name": "stack-inserter",
                "required_recipes": {
                    "advanced-circuit": 3.1578947,
                    "burner-inserter": 0.3245614,
                    "copper-cable": 9.0,
                    "electric-motor": 0.51929825,
                    "fast-inserter": 0.26315789,
                    "inserter": 0.3245614,
                    "iron-gear-wheel": 5.0,
                    "iron-stick": 0.3245614,
                    "motor": 0.38947368,
                    "stack-inserter": 0.26315789,
                    "stone-tablet": 1.25,
                    "electronic-circuit-stone": 5.0,
                    "ltn iron-plate": 23.0,
                    "ltn copper-plate": 18.0,
                    "ltn stone-brick": 2.5,
                    "ltn plastic-bar": 1.0526316,
                },
            },
            {
                "name": "express-transport-belt",
                "required_recipes": {
                    "express-transport-belt": 2.0,
                    "fast-transport-belt": 2.0,
                    "iron-gear-wheel": 23.0,
                    "motor": 1.2,
                    "transport-belt": 1.0,
                    "ltn iron-plate": 96.0,
                    "ltn lubricant": 40.0,
                },
            },
            {
                "name": "solar-panel",
                "required_recipes": {
                    "copper-cable": 11.25,
                    "solar-panel": 10.0,
                    "stone-tablet": 1.875,
                    "electronic-circuit-stone": 7.5,
                    "ltn copper-plate": 27.5,
                    "ltn stone-brick": 3.75,
                    "ltn steel-plate": 5.0,
                    "ltn glass": 5.0,
                },
            },
            {
                "name": "accumulator",
                "required_recipes": {
                    "accumulator": 10.5,
                    "battery": 21.0,
                    "ltn iron-plate": 7.35,
                    "ltn copper-plate": 5.25,
                    "ltn sulfuric-acid": 105.0,
                },
            },
            {
                "name": "electric-furnace",
                "required_recipes": {
                    "advanced-circuit": 12.0,
                    "copper-cable": 5.0,
                    "electric-furnace": 2.0,
                    "se-heat-shielding": 4.0,
                    "steel-furnace": 1.2,
                    "stone-furnace": 0.2,
                    "stone-tablet": 1.8,
                    "sulfur": 1.6,
                    "electronic-circuit-stone": 2.0,
                    "ltn water": 48.0,
                    "ltn stone": 2.0,
                    "ltn copper-plate": 10.0,
                    "ltn stone-brick": 6.0,
                    "ltn steel-plate": 5.2,
                    "ltn petroleum-gas": 48.0,
                    "ltn plastic-bar": 4.0,
                },
            },
            {
                "name": "industrial-furnace",
                "required_recipes": {
                    "advanced-circuit": 5.0,
                    "concrete": 1.0,
                    "copper-cable": 5.9294872,
                    "electric-furnace": 0.32051282,
                    "industrial-furnace": 0.44871795,
                    "iron-stick": 0.05,
                    "processing-unit": 2.5641026,
                    "se-heat-shielding": 4.0,
                    "steel-furnace": 0.25,
                    "stone-furnace": 0.041666667,
                    "stone-tablet": 2.0,
                    "sulfur": 1.6,
                    "electronic-circuit-stone": 3.3974359,
                    "ltn water": 58.0,
                    "ltn stone": 0.41666667,
                    "ltn iron-plate": 0.1,
                    "ltn copper-plate": 11.858974,
                    "ltn stone-brick": 5.0,
                    "ltn steel-plate": 2.6461538,
                    "ltn sand": 1.0,
                    "ltn sulfuric-acid": 1.2820513,
                    "ltn petroleum-gas": 48.0,
                    "ltn plastic-bar": 1.6666667,
                },
            },
            {
                "name": "electric-mining-drill",
                "required_recipes": {
                    "burner-mining-drill": 3.3333333,
                    "copper-cable": 9.375,
                    "electric-mining-drill": 3.125,
                    "electric-motor": 5.0,
                    "iron-gear-wheel": 7.0833333,
                    "motor": 1.0,
                    "ltn iron-plate": 42.916667,
                    "ltn copper-plate": 18.75,
                    "ltn stone-brick": 6.6666667,
                },
            },
            {
                "name": "pumpjack",
                "required_recipes": {
                    "copper-cable": 10.5,
                    "electric-motor": 5.6,
                    "iron-gear-wheel": 7.0,
                    "pipe": 3.5,
                    "pumpjack": 3.5,
                    "ltn iron-plate": 42.0,
                    "ltn copper-plate": 21.0,
                    "ltn steel-plate": 10.5,
                },
            },
            {
                "name": "oil-refinery",
                "required_recipes": {
                    "copper-cable": 12.0,
                    "electric-motor": 6.4,
                    "iron-gear-wheel": 4.0,
                    "oil-refinery": 4.2666667,
                    "pipe": 4.0,
                    "ltn iron-plate": 32.0,
                    "ltn copper-plate": 24.0,
                    "ltn stone-brick": 8.0,
                    "ltn steel-plate": 8.0,
                    "ltn glass": 8.0,
                },
            },
            {
                "name": "chemical-plant",
                "required_recipes": {
                    "chemical-plant": 7.0,
                    "copper-cable": 11.0,
                    "electric-motor": 5.8666667,
                    "iron-gear-wheel": 3.6666667,
                    "pipe": 3.5,
                    "ltn iron-plate": 29.0,
                    "ltn copper-plate": 22.0,
                    "ltn stone-brick": 7.0,
                    "ltn steel-plate": 7.0,
                    "ltn glass": 7.0,
                },
            },
        ]

        # Extract all unique recipes
        recipes = set()
        for item in stuff_to_be_made:
            recipes.update(item["required_recipes"].keys())
        recipes = list(recipes)

        # Number of malls
        num_malls = 5

        # Define the optimization problem
        prob = pulp.LpProblem("Mall_Optimization", pulp.LpMinimize)

        # Variables: whether a recipe is assigned to a mall
        recipe_vars = pulp.LpVariable.dicts(
            "Recipe",
            ((recipe, mall) for recipe in recipes for mall in range(num_malls)),
            0,
            1,
            pulp.LpBinary,
        )

        # Variables: whether an item is assigned to a mall
        item_vars = pulp.LpVariable.dicts(
            "Item",
            (
                (item["name"], mall)
                for item in stuff_to_be_made
                for mall in range(num_malls)
            ),
            0,
            1,
            pulp.LpBinary,
        )

        # Objective: Minimize the number of distinct recipes used in each mall
        prob += pulp.lpSum(
            recipe_vars[recipe, mall] for recipe in recipes for mall in range(num_malls)
        )

        # Constraints
        # Each item must be assigned to exactly one mall
        for item in stuff_to_be_made:
            prob += (
                    pulp.lpSum(item_vars[item["name"], mall] for mall in range(num_malls))
                    == 1
            )

        # If an item is assigned to a mall, all its required recipes must also be assigned to the same mall
        for item in stuff_to_be_made:
            for mall in range(num_malls):
                for recipe, quantity in item["required_recipes"].items():
                    prob += item_vars[item["name"], mall] <= recipe_vars[recipe, mall]
        # Every mall needs to make at least 1 item
        for mall in range(num_malls):
            prob += (
                    pulp.lpSum(item_vars[item["name"], mall] for item in stuff_to_be_made)
                    >= 1
            )
        # The sum of the quantity of each recipe assigned to a mall must be at most 128
        # for mall in range(num_malls):
        #     for recipe in recipes:
        #
        #         prob += pulp.lpSum(item_vars[item["name"], mall] * quantity for item in stuff_to_be_made if
        #                            recipe in item["required_recipes"] for recipe, quantity in
        #                            item["required_recipes"].items()) <= 128 * recipe_vars[recipe, mall]
        for recipe in recipes:
            for mall in range(num_malls):
                prob += (
                        pulp.lpSum(
                            item_vars[item["name"], mall]
                            * item["required_recipes"].get(recipe, 0)
                            for item in stuff_to_be_made
                        )
                        <= 128 * recipe_vars[recipe, mall]
                )

        # Solve the problem
        prob.solve()

        # Output the result
        item_assignment = defaultdict(list)
        for item in stuff_to_be_made:
            for mall in range(num_malls):
                if pulp.value(item_vars[item["name"], mall]) == 1:
                    item_assignment[mall].append(item["name"])

        # Print the assignment of items to malls
        for mall, assigned_items in item_assignment.items():
            print(f"Mall {mall + 1}: {assigned_items}")

        # Print the recipes used in each mall
        recipes_used = defaultdict(set)
        for recipe in recipes:
            for mall in range(num_malls):
                if pulp.value(recipe_vars[recipe, mall]) == 1:
                    recipes_used[mall].add(recipe)

        for mall, recipes in recipes_used.items():
            print(f"Mall {mall + 1} uses recipes: {recipes}")

    def build_optimal_ratios(self, products):
        model_finalizer = CargoWagonMallProblem(
            products, max_assemblers=self.max_assemblers
        )
        # Determine the flow of goods through the production line
        production_line_builder = ProductionLineBuilder(
            self.recipe_provider, self.building_resolver, model_finalizer
        )
        line = production_line_builder.build()
        line.print()
        return line


if __name__ == "__main__":
    # from draftsman.env import update
    # update(verbose=True,path='/Users/swozny/Library/Application Support/factorio/mods')  # equivalent to 'draftsman-update -v -p some/path'

    config_path = "config/real_mall.yaml"

    with open(config_path, "r") as file:
        yaml_data = yaml.safe_load(file)

    config = MallMakerConfig(**yaml_data)

    mall_builder = MallMaker(config)
    mall_builder.make_mall()
