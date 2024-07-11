import yaml
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group

from cargo_wagon_mall import cargo_wagon_mall
from config.meta_schema import denormalize_meta_config, MetaConfig

if __name__ == '__main__':
    path = 'config/meta_block_maker.yaml'
    with open('config/meta_block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)
    configs = denormalize_meta_config(MetaConfig(**yaml_data))
    blueprint_strings = []
    for config in configs:
        print(f'Processing config: {config.target_products}')
        g = cargo_wagon_mall(config)
        blueprint_strings.append(g)
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
    print(b.to_string())

