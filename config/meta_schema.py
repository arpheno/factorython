import yaml
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional, Dict

from config.schema import Beacon, CargoWagonMallConfig


class ProductionSite(BaseModel):
    target_products: List


class MetaConfig(BaseModel):
    production_sites: List[ProductionSite]
    max_assemblers: int
    available_resources: List[str]
    building_resolver_overrides: Dict[str, str]
    assembling_machine_modules: List[str]
    beacon: Beacon
    assembly_path: str
    recipe_path: str
    output: str = 'chest'
    unavailable_resources: List[str]=[]
    additional_resources: List[str]=[]


def denormalize_meta_config(config: MetaConfig) -> List[CargoWagonMallConfig]:
    # List to hold all denormalized configurations
    configs = []

    # Iterate over each production site to create separate configs
    for site in config.production_sites:
        config_data = {
            "target_products": site.target_products,
            "max_assemblers": config.max_assemblers,
            "available_resources": config.available_resources,
            "additional_resources": config.additional_resources,
            "unavailable_resources": config.unavailable_resources,
            "building_resolver_overrides": config.building_resolver_overrides,
            "assembling_machine_modules": config.assembling_machine_modules,
            "beacon": config.beacon,
            "assembly_path": config.assembly_path,
            "recipe_path": config.recipe_path,
            "output": config.output
        }
        config = CargoWagonMallConfig(**config_data)
        configs.append(config)
    return configs
if __name__ == '__main__':
    # Read YAML file
    with open('meta_block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Parse YAML data into Pydantic model
    config = MetaConfig(**yaml_data)
    print(config)
    # Print parsed config
