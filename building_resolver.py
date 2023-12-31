from data_structures.assembling_machine import AssemblingMachine
from data_structures.recipe import Recipe
from fake_assembly_machine import FakeAssemblyMachine


class BuildingResolver:
    def __init__(self, crafting_categories, overrides={}):
        self.crafting_categories = crafting_categories
        self.overrides = overrides

    def __call__(self, recipe: Recipe) -> AssemblingMachine:
        override = self.search(self.overrides[recipe.category]) if recipe.category in self.overrides else None
        default = find_fastest_assembler(recipe, self.crafting_categories)
        return override or default

    def search(self, name):
        try:
            building = next((building for category in self.crafting_categories.values() for building in category if
                         building.name == name))
        except:
            print(f"Could not find building {name}")
            raise Exception("Building not found")
        return building


def find_fastest_assembler(recipe, crafting_categories):
    return max(crafting_categories.get(recipe.category, [FakeAssemblyMachine("LTN")]), key=lambda x: x.crafting_speed)


# Write a short unit test for the above function
def test_find_prototype_with_crafting_category():
    # Arrange
    recipe = Recipe(name="test", category="crafting", energy=1, products=[], ingredients=[])
    crafting_categories = {
        "crafting": [FakeAssemblyMachine("crafting"), FakeAssemblyMachine("crafting2", crafting_speed=2)]}
    # Act
    result = find_fastest_assembler(recipe, crafting_categories)
    # Assert
    assert result.name == "crafting2"
