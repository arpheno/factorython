from copy import deepcopy

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


def belt(origin, destination):
    group = Group()
    difference_x = destination[0] - origin[0]
    difference_y = destination[1] - origin[1]


def simple_smelter() -> Blueprint:
    blueprint = Blueprint()
    entities = [
        {'name': 'stone-furnace', 'tile_position': (0, 0)},
        {'name': 'stone-furnace', 'tile_position': (5, 0)},
        {'name': 'transport-belt', 'tile_position': (-2, 0), 'direction': Direction.SOUTH},
        {'name': 'transport-belt', 'tile_position': (-2, 1), 'direction': Direction.SOUTH},
        {'name': 'transport-belt', 'tile_position': (3, 0), 'direction': Direction.SOUTH},
        {'name': 'transport-belt', 'tile_position': (3, 1), 'direction': Direction.SOUTH},
        {'name': 'transport-belt', 'tile_position': (8, 0), 'direction': Direction.SOUTH},
        {'name': 'transport-belt', 'tile_position': (8, 1), 'direction': Direction.SOUTH},
        {'name': 'inserter', 'tile_position': (-1, 0), 'direction': Direction.WEST},
        {'name': 'inserter', 'tile_position': (2, 0), 'direction': Direction.WEST},
        {'name': 'inserter', 'tile_position': (4, 0), 'direction': Direction.EAST},
        {'name': 'inserter', 'tile_position': (7, 0), 'direction': Direction.EAST},
        {'name': 'small-electric-pole', 'tile_position': (-1, 1)},
        {'name': 'small-electric-pole', 'tile_position': (2, 1)},
        {'name': 'small-electric-pole', 'tile_position': (7, 1)},
    ]
    first_row = Group(entities=deepcopy(entities))
    second_row = Group(
        entities=([entity for entity in entities if not entity['name'].startswith('small-electric-pole')]))
    group = Group()
    group.entities.append(first_row)
    second_row.translate(0, 2)
    group.entities.append(second_row)

    for y in range(12):
        group.translate(0, 4)
        blueprint.entities.append(group)
    blueprint.generate_power_connections()
    return blueprint


if __name__ == '__main__':
    print(simple_smelter().to_string())
