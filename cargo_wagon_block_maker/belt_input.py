from draftsman.classes.group import Group
from draftsman.constants import Direction


def belt_input():
    entities = [
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
