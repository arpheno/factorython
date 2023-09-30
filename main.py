import json

from building_resolver import BuildingResolver
from custom_recipes import probe_recipes
from materials import basic_materials, nauvis_materials, se_materials
from production_groups_provider import ProductionGroupsProvider
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from parsing.recipe_parser import parse_recipes
from recipe_provider import RecipeProvider

if __name__ == "__main__":
    recipes_path = "data/recipes.json"
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    recipes = parse_recipes(recipes)
    recipes.extend(probe_recipes)
    nauvis_materials.extend(se_materials)
    building_resolver = BuildingResolver(crafting_categories)
    delivery_cannon = [r.name for r in recipes if "se-delivery-cannon-pack" in r.name]
    inferior_simulations = [
        r.name for r in recipes if "se-simulation" in r.name if not "asbm" in r.name
    ]
    blacklist = inferior_simulations + delivery_cannon + ["coal-liquefaction"]
    recipe_provider = RecipeProvider(
        recipes, basic_materials, nauvis_materials, blacklist
    )

    production_group_provider = ProductionGroupsProvider(recipe_provider)
    packs = production_group_provider.science_packs_4_deepless()
    product_quantities = [(r.name, 1) for r in packs]

    production_line_builder = ProductionLineBuilder(recipe_provider, building_resolver)
    # line = production_line_builder.build([("se-chemical-gel", 1.0)])
    # line = production_line_builder.build([("se-observation-frame-uv", 1.0)])
    # line = production_line_builder.build([("aai-signal-receiver", 1.0)])
    # line = production_line_builder.build([(item,1.0) for item in second])
    # line = production_line_builder.build([("se-biological-science-pack-1", 1.0)])
    line = production_line_builder.build([("space-science-pack", 700.0)])
    # line = production_line_builder.build(product_quantities)
    line.print()
    # connections = production_line_builder.organize(line)
    # blueprint = quick_line(line)
    # print(blueprint)
