import pandas as pd

from recipe import Recipe, Product


class RecipeProvider:
    def __init__(self, recipes, free_materials, nauvis_materials, blacklist):
        self.recipes = recipes
        self.free_materials = [
            Recipe(
                name=f"free {name}",
                ingredients=[],
                products=[Product(name=name, amount=1, type="free")],
                energy=1,
                category="free",
            )
            for name in free_materials]
        self.nauvis_materials = [
            Recipe(
                name=f"nauvis {name}",
                ingredients=[],
                products=[Product(name=name, amount=1, type="nauvis")],
                energy=1,
                category="nauvis",
            )
            for name in nauvis_materials
        ]
        self.blacklist = blacklist

    def as_dataframe(self):
        recipes_df = pd.DataFrame(
            [r.to_series() for r in self.recipes + self.free_materials + self.nauvis_materials]).fillna(0).T
        recipes_df.drop(self.blacklist, axis=1, inplace=True)
        return recipes_df
