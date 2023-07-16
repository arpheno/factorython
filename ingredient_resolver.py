from recipe import Recipe, Ingredient
from recipe_finder import find_recipes_that_make_product


class IngredientResolver:
    def __init__(self, recipe_chooser, recipes, basic_materials=basic_materials):
        self.recipe_chooser = recipe_chooser
        self.recipes = recipes
        self.basic_materials = basic_materials

    def __call__(self, processed_recipe: Recipe) -> [Recipe]:
        ingredient_recipes = {}
        print(f"Resolving {processed_recipe.name}")
        if processed_recipe is None:
            return None
        for i in [r for r in processed_recipe.ingredients if not r.name in self.basic_materials if 'se' in r.name]:
            recipes_that_produce_ingredient = find_recipes_that_make_product(i.name, self.recipes)
            ingredient_recipe = self.recipe_chooser.choose_recipe(recipes_that_produce_ingredient, i.name)
            [product] = [product for product in ingredient_recipe.products if i.name == product.name]
            print(f' chose {ingredient_recipe.name} for {product}')
            if ingredient_recipe:
                ingredient_recipes[product] = self(ingredient_recipe)
        return ingredient_recipes


from collections import defaultdict


class IngredientResolver:
    def __init__(self, recipe_chooser, recipes, basic_materials=basic_materials):
        self.recipe_chooser = recipe_chooser
        self.recipes = recipes
        self.basic_materials = basic_materials
        self.ingredient_basket = defaultdict(lambda: 0)
        self.product_basket = defaultdict(lambda: 0)
        self.basket = defaultdict(lambda: 0)

    def __call__(self, product, processed_recipe: Recipe, quantity=1) -> dict:
        ingredient_recipes = {}
        print('\n')
        print(f"Resolving {processed_recipe.name} to make product {product.name}")
        if processed_recipe is None:
            return {}

        relative_costs = processed_recipe.relative_cost(product)
        relative_products = processed_recipe.relative_products(product)
        for k, v, in relative_products.items():
            print(f'we make {v * quantity} of {k.name} byproduct of {quantity} of {product.name}')
            self.ingredient_basket[k] += v * quantity
            self.basket[k] -= v * quantity
        for k, v, in relative_costs.items():
            print(f'we need {v * quantity} of {k.name} to make {quantity} of {product.name}')
            self.product_basket[k] += v * quantity
            self.basket[k] += v * quantity

        for i in [r for r in processed_recipe.ingredients if r.name in self.basic_materials or not 'se' in r.name]:
            print(f"also needs {i.name} ({i.amount * quantity})")
        for i in [r for r in processed_recipe.ingredients if r.name not in self.basic_materials and 'se' in r.name]:
            recipes_that_produce_ingredient = find_recipes_that_make_product(i.name, self.recipes)
            ingredient_recipe = self.recipe_chooser.choose_recipe(recipes_that_produce_ingredient, i.name)

            if ingredient_recipe:
                [ingredient] = [p for p in ingredient_recipe.products if p.name == i.name]
                print(f"Chose {ingredient_recipe.name} for {ingredient} ")
                ingredient_quantity = quantity * relative_costs[ingredient]
                ingredient_recipes[product] = self(ingredient, ingredient_recipe, ingredient_quantity)
        return ingredient_recipes
