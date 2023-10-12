from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import assembling_machines
from draftsman.prototypes.assembling_machine import AssemblingMachine
from draftsman.prototypes.inserter import Inserter

print(assembling_machines)


def barreler(mode, fluid, amount):
    g = Group()
    request_filters = [
        {"index": 1, "name": f"{fluid}-barrel", "count": amount // 50 + 1} if mode=='empty' else
        {"index": 1, "name": f"empty-barrel", "count": amount // 50 + 1}
    ]
    entities = ents(fluid, mode, request_filters)
    for entity in entities:
        g.entities.append(**entity)
    return g

def ents(fluid, mode, request_filters,d1=Direction.SOUTH,d2=Direction.NORTH):
    entities = [
        {
            "name": "fast-inserter",
            "id": "output_inserter",
            "position": {"x": 1, "y": 2},
            "direction": d1 if mode == "fill" else d2,
        },
        {
            "name": "fast-inserter",
            "id": "input_inserter",
            "position": {"x": -1, "y": 2},
            "direction": d1 if mode == "empty" else d2,
        },
        {
            "name": "se-space-assembling-machine",
            "recipe": f"{mode}-{fluid}-barrel",
            "id": "machine",
            "position": {"x": 0, "y": 0},
            "direction": d1 if mode=='empty' else d2,
        },
        {
            "name": "logistic-chest-requester",
            'id':'requester_chest',
            "position": (-1, 3),
            "request_filters": request_filters,
        },
        {"name": "logistic-chest-active-provider",
         'id':'provider_chest',"position": (1, 3), "bar": 1},
        {"name": "medium-electric-pole", 'id':'power_pole',"position": (0, 3)},
    ]
    return entities


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
