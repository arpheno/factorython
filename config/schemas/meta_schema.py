import yaml
from pydantic import BaseModel
from typing import List, Dict

from config.schemas.schema import CargoWagonMallConfig
from config.schemas.solver import Solver


class ProductionSite(BaseModel):
    target_products: List
    max_assemblers: int = None
    available_resources: List[str] = []
    output: str = None
    unavailable_resources: List[str] = []
    additional_resources: List[str] = []


class MetaConfig(BaseModel):
    production_sites: List[ProductionSite]
    max_assemblers: int
    building_resolver_overrides: Dict[str, str]
    available_resources: List[str]
    solver: Solver = Solver(time_limit=60)
    output: str = 'chest'
    unavailable_resources: List[str] = []
    additional_resources: List[str] = []
    assembly_path: str = 'data/assembly_machine.json'
    recipe_path: str = 'data/recipes.json'
    inserter_type: str = 'stack-filter-inserter'


def denormalize_meta_config(config: MetaConfig) -> List[CargoWagonMallConfig]:
    # List to hold all denormalized configurations
    configs = []

    # Iterate over each production site to create separate configs
    for site in config.production_sites:
        # Create a new config object with the same values as the original config as default
        config_data = {
            "target_products": site.target_products,
            "max_assemblers": site.max_assemblers or config.max_assemblers,
            "available_resources": site.available_resources or config.available_resources,
            "output": site.output or config.output,
            "unavailable_resources": site.unavailable_resources or config.unavailable_resources,
            "additional_resources": site.additional_resources or config.additional_resources,
            "building_resolver_overrides": config.building_resolver_overrides,
            "assembly_path": config.assembly_path,
            "recipe_path": config.recipe_path,
            "solver": config.solver,
            "inserter_type": config.inserter_type,
        }
        # Allow for config-specific overrides


        config = CargoWagonMallConfig(**config_data)
        configs.append(config)
    return configs


if __name__ == '__main__':
    # Read YAML file
    with open('../meta_block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Parse YAML data into Pydantic model
    config = MetaConfig(**yaml_data)
    print(config)
    # Print parsed config
