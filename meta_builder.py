from random import random, randint

import yaml
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group

from cargo_wagon_mall import CargoWagonMall
from config.schemas.meta_schema import denormalize_meta_config, MetaConfig

if __name__ == '__main__':
    # print(logistic_passive_containers)
    path = 'config/robots_and_such_rest.yaml'
    path = 'config/rocket_science_pack.yaml'
    path = 'config/space_suit.yaml'
    # path = 'config/space.yaml'
    with open(path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    configs = denormalize_meta_config(MetaConfig(**yaml_data))
    blueprint_strings = []
    malls = []
    for config in configs:
        print(f'Processing config: {config.target_products}')
        mall=CargoWagonMall(config)
        mall.validate_self()
        malls.append(mall)
    failed_configs=[]
    lines=[]
    for mall in malls:
        try:
            g,line=mall.build_mall()

        except Exception as e:
            raise
            mall.config.solver.time_limit+= randint(-10,10)
            print(e)
            try:
                g=mall.build_mall()
            except Exception as e:
                print(f'Failed to build mall with config: {mall.config.target_products}')
                print(e)
                failed_configs.append(mall.config)
                continue
        blueprint_strings.append(g)
        lines.append(line)

    print(f'Processed {len(configs)} configs.')
    G=Group()
    y=0
    for blueprint in blueprint_strings:
        b=Blueprint(blueprint.to_string())
        _g=Group(entities=b.entities)
        _g.translate(0,y)
        G.entities.append(_g)
        y+=16
    b=Blueprint()
    b.entities.append(G)
    print('Done, printing blueprint.')
    print(b.to_string())
    print("Procssed configs:")
    for config,line in zip(configs,lines):
        print(config.target_products)
        line.print()
    print("Failed configs:")
    for config in failed_configs:
        print(config.target_products )
