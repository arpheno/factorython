import pandas as pd

from data_structures.recipe import Recipe, Product


class RecipeProvider:
    def __init__(self, recipes, free_materials, nauvis_materials, blacklist):
        self.recipes = recipes
        self.free_materials = [
            Recipe(
                name=f"free {name}",
                ingredients=[],
                products=[Product(name=name, amount=100, type="free")],
                energy=0.000001,
                category="free",
            )
            for name in free_materials]
        self.nauvis_materials = [
            Recipe(
                name=f"nauvis {name}",
                ingredients=[],
                products=[Product(name=name, amount=100, type="nauvis")],
                energy=0.000001,
                category="nauvis",
            )
            for name in nauvis_materials
        ]
        self.blacklist = blacklist
    def by_name(self, name):
        for r in self.recipes + self.free_materials + self.nauvis_materials:
            if r.name == name:
                return r
        raise ValueError(f"Recipe {name} not found")
    def name_includes(self, name):
        return [r for r in self.recipes + self.free_materials + self.nauvis_materials if name in r.name]

    def as_dataframe(self):
        recipes_df = pd.DataFrame(
            [r.to_series() for r in self.recipes + self.free_materials + self.nauvis_materials]).fillna(0).T
        recipes_df.drop(self.blacklist, axis=1, inplace=True)
        return recipes_df
