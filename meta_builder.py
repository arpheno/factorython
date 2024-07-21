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
class ParallelMetaBuilder:
    def __init__(self, path):
        with open(path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        self.meta_config = MetaConfig(**yaml_data)
        self.meta_config.validate_mine()
        # After validation, write the config back to a file with the same name
        self.meta_config.update_yaml(path)
        self.failed_configs = []


    def build(self):
        configs = self.meta_config.configs()
        malls = []
        for config in configs:
            print(f'Processing config: {config.target_products}')
            mall = CargoWagonMall(config)
            malls.append(mall)
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
        production_sites,flows= zip(*[mall.compute_flows(line) for mall, line in zip(malls, lines)])
        bps: List[str] = [mall.construct_blueprint_string(line, production_site, flow) for mall, line, production_site, flow in zip(malls, lines, production_sites, flows)]

        print(f'Processed {len(configs)} configs.')
        G = Group()
        y = 0
        for blueprint_string in bps:
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
        for config in self.failed_configs:
            print(config.target_products)
if __name__ == '__main__':
    # print(logistic_passive_containers)
    path = 'config/robots_and_such_rest.yaml'
    path = 'config/rocket_science_pack.yaml'
    path = 'config/pmall.yaml'
    path = 'config/psmall.yaml'
    # path = 'config/space.yaml'
    builder = ParallelMetaBuilder(path)
    builder.build()