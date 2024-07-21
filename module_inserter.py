from collections import Counter
from typing import Dict, List

from draftsman.data.modules import raw

from building_resolver import BuildingResolver
from materials import intermediate_products
from module import Module, ModuleBuilder
from recipe_provider import RecipeProvider


def transformer_factory(name, **kwargs):
    cls = {
        'primitive_module_inserter': PrimitiveModuleInserter,
        'small_beacon': SmallBeacon,
        'building_speed_applier': BuildingSpeedApplier,
        'module_inserter': BuildingSpecificModuleInserter,
    }
    return cls[name](**kwargs)


class Transformer:
    def __init__(self, **kwargs):
        pass

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        return recipe_provider


class PrimitiveModuleInserter(Transformer):
    def __init__(self, modules: Dict[str, Module]):
        self.modules = modules

    def __call__(self, recipe_provider) -> RecipeProvider:
        for recipe in recipe_provider.recipes:
            if 'ltn' in recipe.name:
                continue
            if recipe.name in intermediate_products:
                self.modules['productivity'](recipe)
            else:
                self.modules['speed'](recipe)

        return recipe_provider


def insert_module(recipe_provider, modules: Dict[str, Module]):
    for recipe in recipe_provider.recipes:
        if 'ltn' in recipe.name:
            continue
        if recipe.name in intermediate_products:
            modules['productivity'](recipe)
        else:
            modules['speed'](recipe)

    return recipe_provider


class SmallBeacon(Transformer):
    def __init__(self, modules: List[str], **kwargs):
        module_builder = ModuleBuilder(raw)
        module_spec = Counter(modules)
        self.module = Module(name='none')
        for module in modules:
            self.module += module_builder.build(module)
        self.beacon_power = {'': 0, 'small': 0.5, 'wab': 10}

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        for recipe in recipe_provider.recipes:
            if 'ltn' in recipe.name:
                continue
            module = self.module * 0.5
            # Compare it before and after
            before = recipe.energy
            module(recipe)
            after = recipe.energy
            print(f'{recipe.name} before: {before} after: {after}')
        return recipe_provider


class BuildingSpecificModuleInserter(Transformer):
    def __init__(self, modules: List[str], building_resolver: BuildingResolver, **kwargs):
        module_builder = ModuleBuilder(raw)
        self.modules = modules
        self.speed_module = module_builder.build(next(module for module in modules if 'speed' in module))
        self.building_resolver = building_resolver

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        module_builder = ModuleBuilder(raw)
        for recipe in recipe_provider.recipes:
            if 'ltn' in recipe.name:
                continue
            building = self.building_resolver(recipe)
            module_slots = building.module_specification.module_slots if building.module_specification else 0
            if recipe.name in intermediate_products:
                module = Module(name=f'{building.name}')
                for module_name in self.modules[:module_slots]:
                    module = module + module_builder.build(module_name)
                print(f'assembled module {module} in building {building.name} for recipe {recipe.name}')
                module(recipe)
            else:
                module = self.speed_module * module_slots
                module(recipe)
        return recipe_provider


class BuildingSpeedApplier(Transformer):
    def __init__(self, modules: Dict[str, str], building_resolver: BuildingResolver, **kwargs):
        self.building_resolver = building_resolver

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        for recipe in recipe_provider.recipes:
            if 'ltn' in recipe.name:
                continue
            building = self.building_resolver(recipe)
            recipe.energy = recipe.energy / building.crafting_speed
        return recipe_provider
