from itertools import chain
# Print current python version
import sys
from typing import Dict

from draftsman.classes.blueprint import Blueprint

from cargo_wagon_block_maker.bbmm import BlueprintMakerModule

from itertools import islice

def batched(iterable, n):
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

# Example usage
for batch in batched(range(10), 3):
    print(batch)
class BlueprintMaker:
    def __init__(
            self,
            modules: Dict[str, BlueprintMakerModule],
    ):
        self.modules = modules
    def make_blueprint(self, recipes, output, entity_lookup, flows):
        # recipes is in a form of grouped recipes by 4, so the first two apply to the top row, the second two to the bottom row of a group of 4
        # i need to reshape this into a list of recipes, where the first half is the top row, the second half is the bottom row for the entire row
        # Oh god the horror

        # This reshapes the top/bottom row enumeration of machines into a grouped enumeration of machines
        # This is necessary because the decision making model works on groups and i'm too lazy to change it
        # to the top/bottom row enumeration
        mrecipes = list(chain.from_iterable(zip(batched(recipes, 2))))
        mrecipes = list(chain.from_iterable(mrecipes[::2])) + list(chain.from_iterable(mrecipes[1::2]))
        default_build_args = dict(
            recipe_names=mrecipes,
            import_export=entity_lookup,
            flows=flows,
            outputs=output,
        )

        blueprint = Blueprint()
        built_modules = {}
        for key, module in self.modules.items():
            built_modules[key] = module.build(blueprint=blueprint, **default_build_args)
        blueprint.generate_power_connections(only_axis=True)
        print(blueprint.to_string())
        return blueprint
