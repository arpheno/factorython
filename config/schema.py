import yaml
from pydantic import BaseModel, conlist
from typing import List, Dict


class Beacon(BaseModel):
    type: str
    modules: List[str]


class OutputConfig(BaseModel):
    type: str = 'chest'


class CargoWagonMallConfig(BaseModel):
    target_products: List
    max_assemblers: int
    available_resources: List[str] = []
    additional_resources: List[str] = []
    unavailable_resources: List[str] = []
    building_resolver_overrides: Dict[str, str]
    assembling_machine_modules: List[str]
    beacon: Beacon
    assembly_path: str
    recipe_path: str
    output: str = 'chest'


if __name__ == '__main__':
    # Read YAML file
    with open('block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Parse YAML data into Pydantic model
    config = CargoWagonMallConfig(**yaml_data)

    # Print parsed config
    print(config.json(indent=4))
