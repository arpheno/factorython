import json
from math import ceil
from pprint import pprint
from random import shuffle

from draftsman.constants import Direction
from draftsman.data import modules
from draftsman.data.modules import raw as modules

from building_resolver import BuildingResolver
from cargo_block_maker import cargo_wagon_blueprint
from cargo_wagon_assignment_problem import create_cargo_wagon_assignment_problem
from model_finalizer import CargoWagonProblem
from module import ModuleBuilder
from module_inserter import insert_module
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import build_recipe_provider

first_block = [
    {'name': 'assembling-machine-3',
     'position': {'x': 501.5, 'y': 369.5},
     'recipe': 'copper-cable',
     'items': {'productivity-module-2': 4},
     },
    {'name': 'assembling-machine-3',
     'position': {'x': 504.5, 'y': 369.5},
     'recipe': 'electronic-circuit-stone',
     'items': {'productivity-module-2': 4},
     },
    {'name': 'assembling-machine-3',
     'position': {'x': 501.5, 'y': 376.5},
     'recipe': 'copper-cable',
     'items': {'productivity-module-2': 4},
     },
    {'name': 'assembling-machine-3',
     'position': {'x': 504.5, 'y': 376.5},
     'recipe': 'stone-tablet',
     'items': {'productivity-module-2': 4},
     },

]
entities=[
   {'name': 'stack-inserter',
    'position': {'x': 501.5, 'y': 371.5},
    },
   {'name': 'stack-inserter',
    'position': {'x': 502.5, 'y': 371.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 503.5, 'y': 371.5},
    },
   {'name': 'stack-inserter',
    'position': {'x': 505.5, 'y': 371.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 504.5, 'y': 371.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 506.5, 'y': 371.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 507.5, 'y': 371.5},
    },
   {'name': 'stack-inserter',
    'position': {'x': 509.5, 'y': 371.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 511.5, 'y': 371.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 510.5, 'y': 371.5},
    },
   {'name': 'miniloader-inserter',
    'position': {'x': 500.5, 'y': 373.5},
    'direction': Direction.WEST,
    'override_stack_size': 1,
    },
   {'name': 'miniloader-inserter',
    'position': {'x': 500.5, 'y': 372.5},
    'direction': Direction.WEST,
    'override_stack_size': 1,
    },

   {'name': 'cargo-wagon',
    'position': {'x': 510.0, 'y': 373.0},
    'orientation': 0.25,
    'inventory': {'filters': [{'index': 1, 'name': 'stone-tablet'},
      {'index': 2, 'name': 'copper-plate'},
      {'index': 3, 'name': 'copper-cable'},
      {'index': 4, 'name': 'electronic-circuit'}],
     'bar': 4},
    },
   {'name': 'filter-miniloader-inserter',
    'position': {'x': 512.5, 'y': 373.5},
    'direction': Direction.EAST,
    'override_stack_size': 1,
    'filters': [{'index': 1, 'name': 'electronic-circuit'}],
    },
   {'name': 'transport-belt',
    'position': {'x': 513.5, 'y': 373.5},
    'direction': Direction.EAST,
    },
   {'name': 'transport-belt',
    'position': {'x': 514.5, 'y': 373.5},
    'direction': Direction.EAST,
    },
   {'name': 'stack-inserter',
    'position': {'x': 501.5, 'y': 374.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 502.5, 'y': 374.5},
    },
   {'name': 'stack-inserter',
    'position': {'x': 503.5, 'y': 374.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 504.5, 'y': 374.5},
    },
    {'name': 'assembling-machine-3',
     'position': {'x': 507.5, 'y': 369.5},
     'recipe': 'copper-cable',
     'items': {'productivity-module-2': 4},
     },
    {'name': 'assembling-machine-3',
     'position': {'x': 510.5, 'y': 369.5},
     'recipe': 'electronic-circuit-stone',
     'items': {'productivity-module-2': 4},
     },
   {'name': 'stack-inserter',
    'position': {'x': 507.5, 'y': 374.5},
    'direction': Direction.SOUTH,
    },
   {'name': 'stack-inserter',
    'position': {'x': 506.5, 'y': 374.5},
    },
   {'name': 'assembling-machine-3',
    'position': {'x': 507.5, 'y': 376.5},
    'recipe': 'electronic-circuit-stone',
    'items': {'productivity-module-2': 4},
    },
   {'name': 'stack-inserter',
    'position': {'x': 508.5, 'y': 374.5},
    },
   {'name': 'stack-inserter',
    'position': {'x': 509.5, 'y': 374.5},
    },
   {'name': 'assembling-machine-3',
    'position': {'x': 510.5, 'y': 376.5},
    'recipe': 'copper-cable',
    'items': {'productivity-module-2': 4},
    },
   {'name': 'stack-inserter',
    'position': {'x': 510.5, 'y': 374.5},
    'direction': Direction.SOUTH,
    },
]
def main():
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories, overrides={"crafting": "assembling-machine-3"}
    )
    recipes_path = "data/recipes.json"
    recipe_provider = build_recipe_provider(recipes_path)
    module_builder = ModuleBuilder(modules)
    recipe_provider = insert_module(
        recipe_provider,
        module_builder.build("speed-module-2") * 4
        + module_builder.build("productivity-module-2") * 4,
    )

    model_finalizer = CargoWagonProblem([("advanced-circuit")], max_assemblers=32)
    # model_finalizer = CargoWagonProblem([("electronic-circuit")], max_assemblers=8)
    production_line_builder = ProductionLineBuilder(
        recipe_provider, building_resolver, model_finalizer
    )
    line = production_line_builder.build()
    line.print()
    production_sites=[]
    global_input = {}
    entities=[]
    for production_site in line.production_sites.values():
        if not 'ltn' in production_site.recipe.name:
            for q in range(ceil(production_site.quantity)):
                production_sites.append(production_site.recipe.name)
                products={product.name:product.average_amount for product in production_site.recipe.products}
                ingredients={ingredient.name:-ingredient.amount for ingredient in production_site.recipe.ingredients}
                entity={good : products.get(good,0)+ingredients.get(good,0) for good in products.keys()|ingredients.keys()}
                entities.append(entity)
        else:
            global_input[production_site.recipe.products[0].name]=production_site.quantity*1.1
    pprint(production_sites)
    # production_sites= ['copper-cable']*4+['electronic-circuit-stone']*3+['stone-tablet']
    production_sites=create_cargo_wagon_assignment_problem(entities,global_input,production_sites)
    cargo_wagon_blueprint(production_sites)
    return line


if __name__ == "__main__":
    main()
