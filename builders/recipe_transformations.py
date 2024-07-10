from materials import minable_resources, basic_processing
from module_inserter import BuildingSpecificModuleInserter
from recipe_provider_builder import FreeRecipesAdder, RecipesRemover


def build_recipe_transformations(config, building_resolver):
    module_inserter = BuildingSpecificModuleInserter(
        modules={"productivity": config.assembling_machine_modules[0],
                 "speed": config.beacon.modules[0]},  # This needs to be changed if we want flexible modules
        beacon_type=config.beacon.type,
        building_resolver=building_resolver,
    )
    lookup = {
        'minable_resources': minable_resources,
        'basic_processing': basic_processing,
    }
    available_resources = [FreeRecipesAdder(lookup[x]) for x in config.available_resources]
    return (available_resources +
            [FreeRecipesAdder(config.additional_resources)] +
            [RecipesRemover(config.unavailable_resources)] +
            [module_inserter])
