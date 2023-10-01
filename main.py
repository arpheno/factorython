import json

from building_resolver import BuildingResolver
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import build_recipe_provider


def main():
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(crafting_categories)
    # deal with recipes
    recipes_path = "data/recipes.json"
    recipe_provider = build_recipe_provider(recipes_path)

    production_line_builder = ProductionLineBuilder(recipe_provider, building_resolver)
    line = production_line_builder.build([("se-chemical-gel", 1.0)])
    line.print()
    return line
    # line = production_line_builder.build([("se-observation-frame-uv", 1.0)])
    # line = production_line_builder.build([("aai-signal-receiver", 1.0)])
    # line = production_line_builder.build([(item,1.0) for item in second])
    # line = production_line_builder.build([("se-biological-science-pack-1", 1.0)])
    # line = production_line_builder.build([("space-science-pack", 700.0)])
    # line = production_line_builder.build(product_quantities)
    # connections = production_line_builder.organize(line)
    # blueprint = quick_line(line)
    # print(blueprint)


if __name__ == "__main__":
    main()
