from recipe import Recipe


class BuildingResolver:
    def __init__(self, crafting_categories):
        self.crafting_categories = crafting_categories

    def __call__(self, recipe: Recipe):
        return find_prototype_with_crafting_category(recipe, self.crafting_categories)


def find_prototype_with_crafting_category(recipe, crafting_categories):
    for category, prototype in crafting_categories.items():
        if recipe.category == category:
            return max(crafting_categories[category], key=lambda x: x.crafting_speed)
    return None
