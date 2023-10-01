from random import shuffle

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.entity import Entity
from draftsman.classes.group import Group
from draftsman.constants import Direction


def cargo_block_maker(recipes):
    assert len(recipes) <= 4
    top_assembler = [{
        'name': 'assembling-machine-3',
        'position': {'x': 0, 'y': 0, },
        'recipe': 'copper-cable',
        'items': {'productivity-module-2': 4},
    },
        {'name': 'stack-inserter',
         'position': {'x': -1, 'y': 2},
         'direction': Direction.SOUTH,
         },
        {'name': 'stack-inserter',
         'position': {'x': 0, 'y': 2},
         'direction': Direction.NORTH,
         },
        {'name': 'stack-inserter',
         'position': {'x': 1, 'y': 2},
         'direction': Direction.SOUTH,
         },
    ]
    bottom_assembler = [{
        'name': 'assembling-machine-3',
        'position': {'x': 0, 'y': 0, },
        'recipe': 'copper-cable',
        'items': {'productivity-module-2': 4},
    },
        {'name': 'stack-inserter',
         'position': {'x': -1, 'y': -2},
         'direction': Direction.NORTH,
         },
        {'name': 'stack-inserter',
         'position': {'x': 0, 'y': -2},
         'direction': Direction.SOUTH,
         },
        {'name': 'stack-inserter',
         'position': {'x': 1, 'y': -2},
         'direction': Direction.NORTH,
         },
    ]
    wagon = [
        {'name': 'cargo-wagon',
         'position': {'x': 2.0, 'y': 5.0},
         'orientation': 0.25,
         'inventory': {'filters': [{'index': 1, 'name': 'copper-plate'},
                                   {'index': 2, 'name': 'copper-cable'},
                                   {'index': 3, 'name': 'stone-brick'},
                                   {'index': 5, 'name': 'electronic-circuit'},
                                   {'index': 8, 'name': 'stone-tablet'}],
                       'bar': 8},
         },
        {'name': 'straight-rail',
         'position': {'x': 1.0, 'y': 5.0},
         'direction': Direction.EAST,
         },
        {'name': 'straight-rail',
         'position': {'x': 3.0, 'y': 5.0},
         'direction': Direction.EAST,
         },
    ]
    wagon = Group(entities=wagon)
    block = Group()
    top = Group()
    ass = Group(entities=top_assembler)
    top.entities.append(ass)
    ass.translate(3, 0)
    top.entities.append(ass)
    block.entities.append(top)
    bottom = Group()
    ass = Group(entities=bottom_assembler)
    bottom.entities.append(ass)
    ass.translate(3, 0)
    bottom.entities.append(ass)
    bottom.translate(0, 7)
    block.entities.append(bottom)
    block.translate(0, 1)
    block.entities.append(wagon)
    for machine,recipe in zip(block.find_entities_filtered(name='assembling-machine-3'),recipes):
        machine.recipe=recipe
    return block

def connector():
    entities = [
        {'name': 'stack-inserter',
         'position': {'x': x, 'y': y},
         'direction': Direction.WEST,
         } for (x, y) in [(0, 0), (0, 1), (1, 0), (1, 1)]
    ]
    return Group(entities=entities)

def belt_input():
    entities=[
        {'name': 'miniloader-inserter',
         'position': {'x': 0, 'y': 0},
         'direction': Direction.WEST,
         'override_stack_size': 1,
         },
        {'name': 'miniloader-inserter',
         'position': {'x': 0, 'y': 1},
         'direction': Direction.WEST,
         'override_stack_size': 1,
         }
    ]
    return Group(entities=entities)
def cargo_wagon_blueprint(production_sites:[str]):
    b = Blueprint()
    i = belt_input()
    i.translate(-1,4)
    b.entities.append(i)
    for i in range(len(production_sites)//4):
        active_recipes= production_sites[i*4:(i+1)*4]
        block =cargo_block_maker(active_recipes)
        block.translate(6*i,0)
        c=connector()
        c.translate(6*i+4,4)
        beac= Group(entities=[{'name': 'beacon', 'position': {'x': 4, 'y': -4}, 'items': {'speed-module-2': 8}}])
        block.entities.append(beac)
        beac.translate(0,16)
        block.entities.append(beac)
        b.entities.append(block)
        b.entities.append(c)
    # b.entities.append(c)
    print(b.to_string())

if __name__ == '__main__':
    production_sites= ['copper-cable']*4+['electronic-circuit-stone']*3+['stone-tablet']
    shuffle(production_sites)
    cargo_wagon_blueprint(production_sites)