from typing import List

from recipe import Recipe


class RecipeChooser:
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        pass


class FirstRecipeChooser(RecipeChooser):
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        return recipes[0] if len(recipes) else None


class MaxAmountChooser(RecipeChooser):
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        return max(recipes, key=lambda x: sum(p.amount for p in x.products if p.name ==desired_product)) if len(
            recipes) else None


class OnlyProductChooser(RecipeChooser):
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        # choose the recipe that only makes the product
        return [r for r in recipes if len(r.products) == 1][0] if any([r for r in recipes if len(r.products) == 1]) else None
class ProductIsFirstChooser(RecipeChooser):
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        #choose the recipe that makes the product first
        return [r for r in recipes if r.products[0].name == desired_product][0] if any([r for r in recipes if r.products[0].name == desired_product]) else None
class RecipenameMatchesProductChooser(RecipeChooser):
    #choose the recipe that has the same name as the product
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        return [r for r in recipes if r.name == desired_product][0] if any([r for r in recipes if r.name == desired_product]) else None
#write a recipe chooser that takes a dictionary of products and recipes at construction time, if the desired product is in the dictionary, return the recipe
class DictionaryChooser(RecipeChooser):
    def __init__(self, dictionary:dict):
        self.dictionary = dictionary
    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        #choose the recipe that has the same name as the product

        return self.dictionary[desired_product] if desired_product in self.dictionary else None

class CompositeRecipeChooser(RecipeChooser):
    def __init__(self, recipe_choosers: List[RecipeChooser]):
        self.recipe_choosers = recipe_choosers

    def choose_recipe(self, recipes: List[Recipe], desired_product) -> Recipe:
        for rc in self.recipe_choosers:
            recipe = rc.choose_recipe(recipes, desired_product)
            if recipe:
                return recipe
        return None
