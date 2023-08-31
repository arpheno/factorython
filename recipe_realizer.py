from cell import Cell
from data_structures.recipe import Recipe


class RecipeRealizer:
    def __init__(self, cell: Cell):
        self.cell = cell

    def realize(self, recipe: Recipe):
        ingredients = recipe.ingredients
        products = recipe.products
        fluid_ingredients = [ingredient for ingredient in ingredients if ingredient.type == "fluid"]
        fluid_products = [product for product in products if product.type == "fluid"]
        solid_ingredients = [ingredient for ingredient in ingredients if ingredient.type == "item"]
        solid_products = [product for product in products if product.type == "item"]
        for fluid_ingredient, pump in zip(fluid_ingredients, self.cell.input_pumps):
            pump.control_behavior['circuit_condition']['first_signal']['name'] = fluid_ingredient.name
        for fluid_product, pump in zip(fluid_products, self.cell.output_pumps):
            pump.control_behavior['circuit_condition']['first_signal']['name'] = fluid_product.name
        for solid_ingredient, loader in zip(solid_ingredients, self.cell.input_loaders):
            loader.filters[0]['name'] = solid_ingredient.name
        for solid_product, loader in zip(solid_products, self.cell.output_loaders):
            loader.filters[0]['name'] = solid_product.name
        self.cell.assembly_machine.recipe = recipe.name

