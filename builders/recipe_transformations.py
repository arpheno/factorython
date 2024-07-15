from materials import minable_resources, basic_processing
from module_inserter import BuildingSpecificModuleInserter, transformer_factory
from recipe_provider_builder import FreeRecipesAdder, RecipesRemover


def build_recipe_transformations(config, building_resolver):
    transformers= []
    for transformation in config.transformations:
        transformers.append(transformer_factory(**transformation.dict(),building_resolver=building_resolver))

    lookup = {
        'minable_resources': minable_resources,
        'basic_processing': basic_processing,
    }
    transformers.extend([FreeRecipesAdder(lookup[x]) for x in config.available_resources])
    transformers.extend([FreeRecipesAdder(config.additional_resources)])
    transformers.extend([RecipesRemover(lookup[x]) for x in config.unavailable_resources])

    return transformers
