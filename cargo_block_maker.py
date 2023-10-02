from copy import deepcopy
from random import shuffle

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.entity import Entity
from draftsman.classes.group import Group
from draftsman.constants import Direction


def cargo_block_maker():
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
    for i in range(len(production_sites)//8):
        eight_block = eight_block_maker()
        active_recipes = production_sites[i * 8:(i + 1) * 8]
        for machine,recipe in zip(eight_block.find_entities_filtered(name='assembling-machine-3'),active_recipes):
            machine.recipe=recipe
        eight_block.translate(12*i,0)
        b.entities.append(eight_block)
    # b.entities.append(c)
    print(b.to_string())


def eight_block_maker():
    beac = Group(entities=[{'name': 'beacon', 'position': {'x': 4, 'y': -4}, 'items': {'speed-module-2': 8}}])
    eight_block = Group()
    block = cargo_block_maker()
    c = connector()
    c.translate( 4, 4)
    eight_block.entities.append(block)
    block = deepcopy(block)
    block.translate(6, 0)
    eight_block.entities.append(block)
    eight_block.entities.append(c)
    eight_block.entities.append(beac)
    beac.translate(0, 16)
    eight_block.entities.append(beac)
    return eight_block


if __name__ == '__main__':
    production_sites= ['copper-cable']*4+['electronic-circuit-stone']*3+['stone-tablet']
    shuffle(production_sites)
    cargo_wagon_blueprint(production_sites)