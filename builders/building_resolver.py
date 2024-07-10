from building_resolver import BuildingResolver
from fake_assembly_machine import FakeAssemblyMachine
from parsing.prototype_parser import parse_prototypes


def build_building_resolver(assembly, building_resolver_overrides):
    crafting_categories = parse_prototypes(assembly)
    crafting_categories['researching'] = [FakeAssemblyMachine("lab", 1)]
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides=building_resolver_overrides,
    )
    return building_resolver
