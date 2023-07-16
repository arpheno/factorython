import json

from building_resolver import BuildingResolver
from production_line_builder import ProductionLineBuilder
from prototype_parser import parse_prototypes
from recipe_parser import parse_recipes
from recipe_provider import RecipeProvider

basic_materials = [
    "water",
    "crude-oil",
    "coal",
    "iron-ore",
    "copper-ore",
    "stone",
    "se-vulcanite-block",
    "se-vitamelange-bloom",
    "se-vitamelange-spice",
    "se-vitamelange-extract",
    "se-methane-gas",
]
nauvis_materials = [
    "copper-plate",
    "iron-plate",
    "steel-plate",
    "stone-tablet",
    "stone-brick",
    "petroleum-gas",
    "heavy-oil",
    "light-oil",
    "glass",
    "sulfur",
    "advanced-circuit",
    "plastic-bar",
    "se-data-storage-substrate",
    "lubricant",
    "se-cryonite-slush",
]

if __name__ == "__main__":
    prototypes_path = "data/entity_prototypes.json"
    recipes_path = "data/recipes.json"
    # read both files and store result in variables
    with open(prototypes_path, "r") as f:
        prototypes = json.load(f)
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    crafting_categories = parse_prototypes(prototypes)
    recipes = parse_recipes(recipes)

    building_resolver = BuildingResolver(crafting_categories)
    recipe_provider = RecipeProvider(recipes, basic_materials, nauvis_materials, ['coal-liquefaction'])
    production_line_builder = ProductionLineBuilder(recipe_provider, building_resolver)
    status, optimal_quantities, production_exprs = production_line_builder.build("se-experimental-specimen", 1)
    print("Status:", status)
    print("Optimal Quantities:")
    for transformation, quantity in optimal_quantities.items():
        if quantity > 0.001:
            print(transformation, ":", quantity)

    print("Production:")
    for item, expr in production_exprs.items():
        if expr.value() > 0.001:
            print(item, ":", expr.value())
