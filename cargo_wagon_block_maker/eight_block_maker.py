from copy import deepcopy

from draftsman.classes.group import Group

from cargo_wagon_block_maker.cargo_block_maker import cargo_block_maker


def eight_block_maker():
    beac = Group(entities=[{'name': 'beacon', 'position': {'x': 4, 'y': -4}, 'items': {'speed-module-2': 8}}])
    eight_block = Group()
    block = cargo_block_maker()
    # c = connector()
    # c.translate( 4, 4)
    eight_block.entities.append(block)
    block = deepcopy(block)
    block.translate(6, 0)
    eight_block.entities.append(block)
    eight_block.entities.append(beac)
    beac.translate(0, 16)
    eight_block.entities.append(beac)
    return eight_block
