import json
import math
from itertools import chain

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group

from building_resolver import BuildingResolver
from materials import se_materials, minable_resources, basic_processing
from model_finalizer import ProductionLineProblem
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import (
    build_recipe_provider,
    FreeRecipesAdder,
    apply_transformations,
    RecipesRemover, Barreler,
)
from space.machine import robot_connected_space_machine


def main():
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides={"space-supercomputing-1": "se-space-supercomputer-1"},
    )
    # deal with recipes
    recipes_path = "data/recipes.json"
    recipe_provider = build_recipe_provider(recipes_path)
    recipe_transformations = [
        FreeRecipesAdder(se_materials),
        FreeRecipesAdder(minable_resources),
        FreeRecipesAdder(basic_processing),
        RecipesRemover([f"se-formatting-{x}" for x in range(2, 5)]),
        Barreler(['petroleum-gas', 'lubricant']),
        FreeRecipesAdder(['advanced-circuit', 'se-space-coolant-warm']),
    ]
    recipe_provider = apply_transformations(recipe_provider, recipe_transformations)

    model_finalizer = ProductionLineProblem(
        [("se-biological-science-pack-4", 2000.0 / 3600)]
    )
    model_finalizer = ProductionLineProblem([("se-bio-sludge", 20)])
    production_line_builder = ProductionLineBuilder(
        recipe_provider, building_resolver, model_finalizer
    )
    line = production_line_builder.build()
    line.print()
    line.print(duration=3600)
    b = Blueprint()
    width = 150
    production_sites = list(chain.from_iterable(
        [[production_site] * math.ceil(production_site.quantity) for production_site in line.production_sites.values()
         if not any(x in production_site.recipe.name for x in ['ltn', 'empty-'])]))

    square_length = next(x for x in range(10) if x * x >= len([p for p in production_sites]))
    rows = [Group() for _ in range(square_length)]
    for i, production_site in enumerate(production_sites):
        g = rows[i // square_length]
        if any(x in production_site.recipe.name for x in ['ltn', 'empty-']):
            continue
        print(f'making blueprint for {production_site.recipe.name} in building {production_site.building.name}')
        try:
            machine = robot_connected_space_machine(building_resolver, recipe_provider, production_site.recipe.name)
            max_x = max(
                [(e.global_position['x'], e.tile_width // 2 + 1, e.name) for e in g.find_entities_filtered()] + [
                    (0, 0)])
            min_local_x = min([(e.global_position['x'], +e.tile_width // 2 + 1, e.name) for e in
                               machine.find_entities_filtered()])
            print(max_x, min_local_x)
            original_x_coordinate = math.ceil(max_x[0] + max_x[1] + abs(min_local_x[0]) + min_local_x[1])
            machine.translate(original_x_coordinate, 0)
            g.entities.append(machine)
        except:
            print(
                f'could not make blueprint for {production_site.recipe.name} in building {production_site.building.name}')
            continue
    for i, row in enumerate(rows):
        row.translate(0, 20 * i)
        b.entities.append(row)
    b.generate_power_connections()
    print(b.to_string())
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
