import json
from collections import defaultdict
from functools import partial, reduce

import matplotlib.pyplot as plt
from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction

from cell import Cell
from data_structures.recipe import Recipe
from recipe_realizer import RecipeRealizer

pumps = defaultdict(dict)


def visualize(entities):
    x_coordinates = [entity.position[0] for entity in entities]
    y_coordinates = [entity.position[1] for entity in entities]
    labels = [entity.name for entity in entities]
    plt.figure(figsize=(8, 6))
    plt.scatter(x_coordinates, y_coordinates, marker='o', s=100)

    for i, label in enumerate(labels):
        plt.text(x_coordinates[i], y_coordinates[i], label, fontsize=10, ha='right', va='bottom')

    # Invert the y-axis and set the limits
    plt.gca().invert_yaxis()
    # plt.ylim(plt.ylim()[::-1])

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('X-Y Distribution of Entities')
    plt.grid(True)
    plt.show()


def compose(*funcs):
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


accessors = {
    f: {
        coord: partial(f, key=lambda x: x.position[coord])
        for coord in [0, 1]}
    for f in (min, max, sorted)
}


def build_cell(blueprint):
    solid_order = ['stone', 'iron-ore', 'copper-ore', 'uranium-ore']
    liquid_order = ['water', 'crude-oil', 'heavy-oil', 'light-oil']
    pumps = blueprint.find_entities_filtered(name="pump")
    output_pumps = compose(accessors[sorted][0], accessors[sorted][1])(pumps)[4::-1]
    input_pumps = compose(accessors[sorted][0], accessors[sorted][1])(pumps)[:4]
    pump_setting = lambda pump: pump.control_behavior['circuit_condition']['first_signal']['name']
    input_pumps = sorted(input_pumps, key=lambda pump: liquid_order.index(pump_setting(pump)))
    output_pumps = sorted(output_pumps, key=lambda pump: liquid_order.index(pump_setting(pump)))
    loaders = blueprint.find_entities_filtered(name='space-filter-miniloader-inserter')
    input_loaders = compose(accessors[sorted][0], accessors[sorted][1])(loaders)[:4]
    middle_loaders = compose(accessors[sorted][0], accessors[sorted][1])(loaders)[4:8]
    output_loaders = compose(accessors[sorted][0], accessors[sorted][1])(loaders)[8:]
    loader_setting = lambda loader: loader.filters[0]['name']
    key = lambda loader: solid_order.index(loader_setting(loader))
    input_loaders = sorted(input_loaders, key=key)
    middle_loaders = sorted(middle_loaders, key=key)
    output_loaders = sorted(output_loaders, key=lambda loader: loader.position[0])
    combinators = blueprint.find_entities_filtered(name='ltn-combinator')
    combinators = accessors[sorted][1](combinators)
    assembly_machine = blueprint.find_entities_filtered(type='assembling-machine')[0]
    return Cell(input_loaders=input_loaders,
                middle_loaders=middle_loaders,
                output_loaders=output_loaders,
                input_pumps=input_pumps,
                output_pumps=output_pumps,
                combinators=combinators,
                assembly_machine=assembly_machine)


if __name__ == '__main__':
    with open('data/cell_blueprint.json') as f:
        blueprint = Blueprint(f.read())
    cell = build_cell(blueprint)

    recipes_path = "data/recipes.json"
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    [recipe] = [recipe for key, recipe in recipes.items() if recipe['name'] == 'se-chemical-gel']
    recipe_realizer = RecipeRealizer(cell)
    recipe_realizer.realize(Recipe(**recipe))
    result = blueprint.to_string()
    print(result)
