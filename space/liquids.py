import math
import warnings

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import assembling_machines
from draftsman.error import InvalidRecipeError
from draftsman.prototypes.assembling_machine import AssemblingMachine
from draftsman.prototypes.inserter import Inserter

print(assembling_machines)


def barreler(mode, fluid, amount, provider_chest_name="logistic-chest-active-provider"):
    request_filters = [
        {"index": 1, "name": f"{fluid}-barrel", "count": math.ceil(amount // 50 + 1)} if mode == 'empty' else
        {"index": 1, "name": f"empty-barrel", "count": math.ceil(amount // 50 + 1)}
    ]
    entities = [
        {
            "name": "fast-inserter",
            "id": "output_inserter",
            "position": {"x": 1, "y": 2},
            "direction": Direction.NORTH,
        },
        {
            "name": "fast-inserter",
            "id": "input_inserter",
            "position": {"x": -1, "y": 2},
            "direction": Direction.SOUTH,
        },
        {
            "name": "se-space-assembling-machine",
            "recipe": f"{mode}-{fluid}-barrel",
            "id": "machine",
            "position": {"x": 0, "y": 0},
            "direction": Direction.SOUTH if mode == 'empty' else Direction.NORTH
        },
        {
            "name": "logistic-chest-requester",
            'id': 'requester_chest',
            "position": (-1, 3),
            "request_filters": request_filters,
        },
        {"name": provider_chest_name,
         'id': 'provider_chest',
         "position": (1, 3), "bar": 1},
            {"name": "medium-electric-pole", 'id': 'power_pole', "position": (0, 3)},
        ]
    try:
        g = Group()
        for entity in entities:
            g.entities.append(**entity)
    except InvalidRecipeError:
        g = Group()
        warnings.warn(f'Cannot barrel {fluid}')
    return g


if __name__ == "__main__":
    k = AssemblingMachine("assembling-machine-3")
    b = Blueprint()
    barr = barreler("fill", "lubricant", 1000)
    b.entities.append(barr)
    barr = barreler("empty", "lubricant", 1000)
    barr.translate(5, 0)
    barr.rotate(2)
    b.entities.append(barr)
    barr = barreler("empty", "lubricant", 1000)
    barr.translate(10, 0)
    barr.rotate(4)
    b.entities.append(barr)
    print(b.to_string())
