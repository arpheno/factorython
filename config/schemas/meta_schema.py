import difflib
import json
from collections import OrderedDict

import yaml
from rapidfuzz import process, fuzz

from builders.building_resolver import build_building_resolver
from builders.recipe_transformations import build_recipe_transformations
from cargo_wagon_mall import CargoWagonMall
from config.schemas.schema import CargoWagonMallConfig, Transformation
from pydantic import BaseModel, field_validator, model_validator, Extra
from typing import List, Dict

from config.schemas.solver import Solver
from recipe_provider_builder import build_recipe_provider


class ProductionSite(BaseModel):
    target_products: Dict[str, int]
    max_assemblers: int = 32
    available_resources: List[str] = []
    output: str = 'chest'
    unavailable_resources: List[str] = []
    additional_resources: List[str] = []


class MetaConfig(BaseModel,extra=Extra.forbid):
    production_sites: List[ProductionSite]
    max_assemblers: int
    building_resolver_overrides: Dict[str, str]
    inserter_type: str = 'stack-filter-inserter'
    transformations: List[Transformation] = []
    available_resources: List[str]
    solver: Solver = Solver(time_limit=60)
    output: str = 'chest'
    unavailable_resources: List[str] = []
    additional_resources: List[str] = []
    assembly_path: str = 'data/assembly_machine.json'
    recipe_path: str = 'data/recipes.json'
    # We want to validate production sites first

    def configs(self) -> List[CargoWagonMallConfig]:
        # List to hold all denormalized configurations
        configs = []

        # Iterate over each production site to create separate configs
        for site in self.production_sites:
            # Create a new config object with the same values as the original config as default
            config_data = {
                "target_products": site.target_products,
                "max_assemblers": site.max_assemblers or self.max_assemblers,
                "available_resources": site.available_resources or self.available_resources,
                "output": site.output or self.output,
                "unavailable_resources": site.unavailable_resources or self.unavailable_resources,
                "additional_resources": site.additional_resources or self.additional_resources,
                "building_resolver_overrides": self.building_resolver_overrides,
                "transformations": self.transformations,
                "assembly_path": self.assembly_path,
                "recipe_path": self.recipe_path,
                "solver": self.solver,
                "inserter_type": self.inserter_type,
            }
            # Allow for self-specific overrides

            config = CargoWagonMallConfig(**config_data)
            configs.append(config)
        return configs

    def validate_mine(self):
        config = self
        assembly = json.load(open(config.assembly_path))
        building_resolver = build_building_resolver(assembly, config.building_resolver_overrides)

        recipes = json.load(open(config.recipe_path))
        _recipe_provider = build_recipe_provider(recipes, building_resolver)
        _recipe_transformations = build_recipe_transformations(config, building_resolver)

        recipe_names = [recipe.name for recipe in
                        _recipe_provider.recipes]  # Assuming recipes is a list of dicts with 'name' key
        for site in config.production_sites:
            print(f'Validating {site.target_products}')
            new_target_products = {}
            for product, q in site.target_products.items():
                try:
                    _recipe_provider.by_name(product)
                    new_target_products[product] = q
                except ValueError:
                    # If exact match is not found, use rapidfuzz to find the closest match
                    closest_matches = process.extract(product, recipe_names, scorer=fuzz.ratio, limit=5)
                    suggestions = [(match[0], match[1]) for match in closest_matches]
                    print(f"Recipe '{product}' not found. Did you mean: ")
                    for i, (suggestion, score) in enumerate(suggestions):
                        print(f"{i}. {suggestion} with score {score}")
                    # Ask user to write the number of the correct recipe with input:
                    correct_recipe = input("Enter the number of the correct recipe: ")
                    if len(correct_recipe) == 0:
                        closest_matches = process.extract(product, recipe_names, scorer=fuzz.ratio, limit=20)
                        suggestions = [(match[0], match[1]) for match in closest_matches]
                        for i, (suggestion, score) in enumerate(suggestions):
                            print(f"{i}. {suggestion} with score {score}")
                        # Ask user to write the number of the correct recipe with input:
                        correct_recipe = input("Enter the number of the correct recipe: ")
                    # Replace the product with the correct recipe
                    # find the index of the product in the list and replace it with the closest match
                    reco, score, _ = closest_matches[int(correct_recipe)]
                    new_target_products[reco] = q
            site.target_products = new_target_products

    def save_to_yaml(self, output_path: str):
        # Custom YAML dumper to write list items on the same line
        class MyDumper(yaml.Dumper):
            def increase_indent(self, flow=False, indentless=False):
                return super(MyDumper, self).increase_indent(flow, False)

        # Save the current state of the config to a YAML file
        with open(output_path, 'w') as file:
            yaml.dump(self.dict(), file, Dumper=MyDumper, default_flow_style=False)

    # def update_yaml(self, output_path: str):
    #     with open(output_path, 'r') as file:
    #         yaml_data = yaml.safe_load(file)
    #     for file_state, new_state in zip(yaml_data['production_sites'], self.production_sites):
    #         for key, value in new_state.target_products.items():
    #             file_state['target_products'][key] = value
    #     with open(output_path, 'w') as file:
    #         yaml.dump(yaml_data, file, default_flow_style=False)

    def update_yaml_old(self, output_path: str):
        # Read the original file and keep its content for diff
        with open(output_path, 'r') as file:
            original_content = file.readlines()  # Read the original content for diff generation
            file.seek(0)  # Reset file pointer to the start
            yaml_data = yaml.safe_load(file)

        # Update YAML data
        for file_state, new_state in zip(yaml_data['production_sites'], self.production_sites):
            print(f'Updating {file_state["target_products"]} with {new_state.target_products}')
            file_state['target_products']=new_state.target_products

        # Write the updated YAML data to the file
        with open(output_path, 'w') as file:
            yaml.dump(yaml_data, file, default_flow_style=False)

        # Read the updated content for diff
        with open(output_path, 'r') as file:
            updated_content = file.readlines()

        # Generate diff
        diff = difflib.unified_diff(original_content, updated_content, fromfile='before_update.yaml',
                                    tofile='after_update.yaml')
        print(''.join(diff))

    def to_ordered_dict(self):
        data = OrderedDict()
        for field in self.__fields__:
            value = getattr(self, field)
            if isinstance(value, BaseModel):
                value = value.dict()
            data[field] = value
        return data

    def update_yaml(self, output_path: str):
        # Read the original file and keep its content for diff
        with open(output_path, 'r') as file:
            original_content = file.readlines()  # Read the original content for diff generation
            file.seek(0)  # Reset file pointer to the start
            yaml_data = yaml.safe_load(file)

        # Update YAML data
        for file_state, new_state in zip(yaml_data['production_sites'], self.production_sites):
            print(f'Updating {file_state["target_products"]} with {new_state.target_products}')
            file_state['target_products'] = new_state.target_products
        reordered_dict = {k: yaml_data[k] for k in self.__fields__ if k in yaml_data}

        # Write the updated YAML data to the file
        with open(output_path, 'w') as file:
            yaml.dump(reordered_dict, file, default_flow_style=False,sort_keys=False)

        # Read the updated content for diff
        with open(output_path, 'r') as file:
            updated_content = file.readlines()

        # Generate diff
        diff = difflib.unified_diff(original_content, updated_content, fromfile='before_update.yaml',
                                    tofile='after_update.yaml')
        print(''.join(diff))


if __name__ == '__main__':
    # Read YAML file
    with open('../meta_block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Parse YAML data into Pydantic model
    config = MetaConfig(**yaml_data)
    print(config)
    # Print parsed config
