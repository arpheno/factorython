import random
from typing import Dict, Any

from draftsman.classes.blueprint import Blueprint

from cargo_wagon_block_maker import eight_block_maker, filter_connector
from cargo_wagon_block_maker.belt_input import belt_input
from cargo_wagon_block_maker.filter_connector import filter_connector_4


def cargo_wagon_blueprint(production_sites: [str], machines: Dict[Any, Dict[str, float]], output):
    b = Blueprint()
    i = belt_input()
    i.translate(-1, 4)
    b.entities.append(i)
    assert len(production_sites) > 8
    for i in range(len(production_sites) // 8):
        eight_block = eight_block_maker.eight_block_maker()
        active_recipes = production_sites[i * 8:(i + 1) * 8]
        for machine, recipe in zip(eight_block.find_entities_filtered(name='assembling-machine-3'), active_recipes):
            machine.recipe = recipe
        eight_block.translate(12 * i, 0)
        b.entities.append(eight_block)

    # Add a connector to connect in between the blocks
    straight_rails = b.find_entities_filtered(name='straight-rail')
    # order them by x pos
    straight_rails = sorted(straight_rails, key=lambda rail: rail.global_position.x)
    # Theres gaps between the rails, find them all
    gaps = []
    for rail2 in straight_rails[1::2][:-1]:
        gaps.append(rail2.global_position.x + 1)
        print(f'gap at {gaps[-1]}')

    # Set wagons filters according to the production sites going from the back to the front
    # Sort the wagons by their x position in inverse order
    wagons = sorted(b.find_entities_filtered(name='cargo-wagon'), key=lambda wagon: -wagon.global_position.x)

    # sort production sites inverse and yield chunks of 4
    # yield chunks of 4
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    production_sites_around_wagon = reversed(list(chunks(production_sites, 4)))
    all_filters = set()
    filters = []
    for wagon, production_sites in zip(wagons, production_sites_around_wagon):
        # create a set of all keys in the entities of the production site
        items_used_in_block = set(
            sum((list(machines[production_site].keys()) for production_site in production_sites), []))
        all_filters.update(items_used_in_block)
        filters.append(items_used_in_block)
        # set the filters of the wagon
        wagon.inventory['filters'] = [{'index': i + 1, 'name': item} for i, item in enumerate(all_filters)]
        # set bar to the number of filters
        wagon.inventory['bar'] = len(all_filters)
    for gap, filter in zip(gaps[::-1], filters):
        if len(filter) == 4:
            print("We can be smart about inserters")
            c = filter_connector_4(*filter)
        elif len(filter - {output}) < 5:
            print("We can be smart about inserters, but need an output line")
            c = filter_connector_4(*(filter - {output}))
        else:
            print("Damn, too many goods")
            choice = random.sample(filter - {output}, 2)
            c = filter_connector(*choice)
        c.translate(gap, 4)
        b.entities.append(c)

    print(b.to_string())
