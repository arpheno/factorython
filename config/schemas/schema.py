from typing import List, Dict
from pydantic import BaseModel
import yaml

from config.schemas.solver import Solver


class Beacon(BaseModel):
    type: str
    modules: List[str]

class OutputConfig(BaseModel):
    type: str = 'chest'

class Transformation(BaseModel):
    name: str
    modules: List[str] = []

class CargoWagonMallConfig(BaseModel):
    target_products: List[List]  # List of lists to accommodate [1, fast-inserter]
    max_assemblers: int
    available_resources: List[str] = []
    additional_resources: List[str] = []
    unavailable_resources: List[str] = []
    assembling_machine_modules: List[str] = []
    building_resolver_overrides: Dict[str, str]
    beacon: Beacon = None
    transformations: List[Transformation] = []
    assembly_path: str
    recipe_path: str
    output: str = 'chest'
    inserter_type: str = 'stack-filter-inserter'
    inserter_capacity_bonus: int = 0
    solver: Solver = Solver(time_limit=30)

if __name__ == '__main__':
    # Read YAML file
    with open('../block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Parse YAML data into Pydantic model
    config = CargoWagonMallConfig(**yaml_data)

    # Print parsed config
    print(config.json(indent=4))
