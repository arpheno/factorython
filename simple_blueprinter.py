from draftsman.classes.blueprint import Blueprint
from draftsman.classes.entity import Entity
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import containers, logistic_request_containers, assembling_machines, \
    logistic_passive_containers, inserters, electric_poles

print(electric_poles)
from data_structures.recipe import Recipe
from production_line import ProductionLine


def quick_line(line: ProductionLine):
    blueprint = Blueprint()
    groups = []
    for name, production_site in line.production_sites.items():
        if 'nauvis' in name or 'free' in name:
            continue
        group = quick_machine(production_site.recipe)
        groups.append(group)

    x, y = 0, 0
    length = 5
    targets = []
    for i in range(len(groups)):
        target_x = 3 * (i % length)
        target_y = 5 * (i // length)
        targets.append((target_x, target_y))
    for target, group in zip(targets, groups):
        group.translate(*target)
        blueprint.entities.append(group)
        maximum_x = max([entity.position['x'] for group in blueprint.entities for entity in group.entities])
        x = maximum_x + 1
        print(x)
    return blueprint.to_string()


def quick_machine(recipe: Recipe):
    request_filters = [{'index': i,
                        'name': ingredient.name,
                        'count': int(ingredient.amount / recipe.energy * 45)
                        } for i, ingredient in enumerate(recipe.ingredients)]
    assembly_machine_map = {'crafting': 'assembling-machine-3',
                            'lifesupport': 'se-lifesupport-facility'}
    group = Group()
    entities = [
        {'name': assembly_machine_map[recipe.category], 'tile_position': (0, 0), 'recipe': recipe.name},
        {'name': 'logistic-chest-requester', 'tile_position': (0, 4),
         'request_filters': request_filters},
        {'name': 'logistic-chest-passive-provider', 'tile_position': (2, 4), 'bar': 1},
        {'name': 'medium-electric-pole', 'tile_position': (1, 4)},
        {'name': 'fast-inserter', 'tile_position': (0, 3), 'direction': Direction.SOUTH},
        {'name': 'fast-inserter', 'tile_position': (2, 3), 'direction': Direction.NORTH},
    ]
    for entity in entities:
        group.entities.append(**entity)
    return group
