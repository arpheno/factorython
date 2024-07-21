import yaml

from cargo_wagon_mall import CargoWagonMall
from config.schemas.schema import CargoWagonMallConfig

if __name__ == "__main__":
    # from draftsman.env import update
    # update(verbose=True,path='/Users/swozny/Library/Application Support/factorio/mods')  # equivalent to 'draftsman-update -v -p some/path'

    config_path = "config/small_block_maker.yaml"

    with open(config_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    config = CargoWagonMallConfig(**yaml_data)

    mall_builder = CargoWagonMall(config)
    mall_builder.build_mall()
