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
    top.translate(-1, 0)
    block.entities.append(top)
    bottom = Group()
    ass = Group(entities=bottom_assembler)
    bottom.entities.append(ass)
    ass.translate(3, 0)
    bottom.entities.append(ass)
    bottom.translate(-1, 7)
    block.entities.append(bottom)
    block.translate(0, 1)
    block.entities.append(wagon)
    return block
