from collections import Counter
from multiprocessing import Pool
from random import random, randint

import yaml
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from typing import List

from cargo_wagon_mall import CargoWagonMall
from config.schemas.meta_schema import MetaConfig
from parallel_stuff import generate_blueprints
from production_line import ProductionLine

if __name__ == '__main__':
    # print(logistic_passive_containers)
    path = 'config/robots_and_such_rest.yaml'
    path = 'config/rocket_science_pack.yaml'
    path = 'config/pmall.yaml'
    # path = 'config/space.yaml'
    with open(path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    meta_config = MetaConfig(**yaml_data)
    meta_config.validate_mine()
    # After validation, write the config back to a file with the same name
    meta_config.update_yaml(path)

    configs = meta_config.configs()
    malls = []
    for config in configs:
        print(f'Processing config: {config.target_products}')
        mall = CargoWagonMall(config)
        malls.append(mall)
    failed_configs = []
    # Let's process the malls in parallel
    p = Pool(4)
    lines: List[ProductionLine] = p.map(CargoWagonMall.build_optimal_ratios, malls)

    for config, line in zip(configs, lines):
        print(config.target_products)
        line.print()
    ltn_supply = Counter()
    for line in lines:
        for product, site in line.ltn_input.items():
            ltn_supply[product] += site.quantity
    print("LTN Supply:")
    for product, quantity in ltn_supply.items():
        print(f'{product}: {quantity}')

    blueprint_strings = generate_blueprints(malls, lines)

    print(f'Processed {len(configs)} configs.')
    G = Group()
    y = 0
    for blueprint_string in blueprint_strings:
        b = Blueprint(blueprint_string)
        _g = Group(entities=b.entities)
        _g.translate(0, y)
        G.entities.append(_g)
        y += 16
    b = Blueprint()
    b.entities.append(G)
    print('Done, printing blueprint.')
    print(b.to_string())
    print("Procssed configs:")
    for config, line in zip(configs, lines):
        print(config.target_products)
        line.print()
    print("Failed configs:")
    for config in failed_configs:
        print(config.target_products)
