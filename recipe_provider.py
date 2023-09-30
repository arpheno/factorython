import pandas as pd

from data_structures.recipe import Recipe, Product


class RecipeProvider:
    def __init__(self, recipes, ltn_materials, blacklist):
        self.recipes = recipes
        self.recipes.extend([
            Recipe(
                name=f"ltn {name}",
                ingredients=[],
                products=[Product(name=name, amount=1, type="free")],
                energy=1,
                category="free",
            )
            for name in ltn_materials])
        self.blacklist = blacklist

    def by_name(self, name):
        for r in self.recipes:
            if r.name == name:
                return r
        raise ValueError(f"Recipe {name} not found")

    def name_includes(self, name):
        return [r for r in self.recipes if name in r.name]

    def as_dataframe(self):
        recipes_df = pd.DataFrame(
            [r.to_series() for r in self.recipes]).fillna(0).T
        recipes_df.drop(self.blacklist, axis=1, inplace=True)
        return recipes_df
