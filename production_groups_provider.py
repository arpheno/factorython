from recipe_provider import RecipeProvider


class ProductionGroupsProvider:
    def __init__(self, recipe_provider: RecipeProvider):
        self.recipe_provider = recipe_provider

    def science_packs_4(self):
        four_packs = self.recipe_provider.name_includes("science-pack-4")
        other_packs = [
            self.recipe_provider.by_name(r)
            for r in [
                "se-rocket-science-pack",
                "utility-science-pack",
                "production-science-pack",
            ]
        ]
        return four_packs + other_packs
    def science_packs_4_deepless(self):
        return [r for r in self.science_packs_4() if not "deep" in r.name]

    def catalogues(self):
        return self.recipe_provider.name_includes("catalogue")
