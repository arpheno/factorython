from typing import List, Union, Dict

import pandas as pd
from pydantic import BaseModel
import pytest

from typing import Optional
from pydantic import BaseModel, validator


class Product(BaseModel):
    type: str
    name: str
    amount: Optional[Union[float, int]] = None
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    probability: Optional[float] = 1

    @property
    def average_amount(self) -> float:
        if self.amount is not None:
            return float(self.amount) * self.probability
        elif self.amount_min is not None and self.amount_max is not None and self.probability is not None:
            return float(self.amount_min + self.amount_max) / 2 * self.probability
        else:
            raise ValueError("Product has no amount")

    def __str__(self):
        return f"type={self.type} amount={self.average_amount} name={self.name}"

    def __eq__(self, other):
        # check based on name
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __mul__(self, other):
        return Product(type=self.type, amount=self.average_amount * other, name=self.name)


class Ingredient(BaseModel):
    type: str
    amount: float
    name: str

    def __mul__(self, other):
        return Ingredient(type=self.type, amount=self.amount * other, name=self.name)

    def __imul__(self, other):
        self.amount *= other
        return self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        # check based on name
        return self.name == other.name


class Item(BaseModel):
    type: str
    amount: float
    name: str

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        # check based on name
        return self.name == other.name


class MultiplicableDict(dict):
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return MultiplicableDict({key: value * other for key, value in self.items()})
        else:
            raise ValueError("Multiplication is only supported with numbers (int or float).")

    def __rmul__(self, other):
        return self.__mul__(other)


class Recipe(BaseModel):
    name: str
    category: str
    products: List[Product]
    ingredients: List[Ingredient]
    energy: float

    def summary(self) -> MultiplicableDict[str, float]:
        """
        Returns a summary of the recipe in the form of a dictionary
        Example:
        {
            "iron-plate": 1,
            "copper-plate": 0.5,
            "iron-ore": -1
        }
        Positive values are things that are produced, negative values are things that are consumed
        """
        products = {
            product.name: product.average_amount
            for product in self.products
        }
        ingredients = {
            ingredient.name: -ingredient.amount
            for ingredient in self.ingredients
        }

        entity = {
            good: products.get(good, 0) + ingredients.get(good, 0)
            for good in products.keys() | ingredients.keys()
        }
        return MultiplicableDict(entity)

    def average_amount(self, product: Product):
        return next((p.average_amount for p in self.products if p.name == product.name), None)

    def __str__(self):
        products_str = "\n  - ".join([str(product) for product in self.products])
        ingredients_str = "\n  - ".join([str(ingredient) for ingredient in self.ingredients])

        return f"Recipe: {self.name}\n" \
               f"Category: {self.category}\n" \
               f"Products:\n  - {products_str}\n" \
               f"Ingredients:\n  - {ingredients_str}\n" \
               f"Energy: {self.energy}\n"

    def to_series(self):
        inputs = pd.Series({i.name: i.amount for i in self.ingredients})
        outputs = pd.Series({p.name: p.average_amount for p in self.products})
        result = outputs.subtract(inputs, fill_value=0)
        result.name = self.name
        return result

    def __hash__(self):
        return hash(self.name)
# i want a new EmbeddedRecipe class that is a subclass of Recipe but has a new field called building
class EmbeddedRecipe(Recipe):
    building: str

    def __str__(self):
        return super().__str__() + f"Building: {self.building}\n"

    def to_series(self):
        result = super().to_series()
        result['building'] = self.building
        return result

    def __hash__(self):
        return hash((self.name, self.building))

