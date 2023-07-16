from typing import List, Union

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
            return None

    def __eq__(self, other):
        # check based on name
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"{self.name}"


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


class Recipe(BaseModel):
    name: str
    category: str
    products: List[Product]
    ingredients: List[Ingredient]
    energy: float

    def average_amount(self, product: Product):
        return next((p.average_amount for p in self.products if p.name == product.name), None)

    def relative_cost(self, product: Product):
        # return how expensive a unit of product is in terms of all ingredients
        result = {i: (i.amount / product.average_amount) for i in self.ingredients}
        return result

    def relative_products(self, product: Product):
        # return how expensive a unit of product is in terms of all ingredients
        result = {i: (i.average_amount / product.average_amount) for i in self.products}
        return result

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
        if None in inputs.index or None in outputs.index:
            print('?')
        if None in inputs.values or None in outputs.values:
            print('?')
        result = outputs.subtract(inputs, fill_value=0)
        result.name = self.name
        return result

    def __hash__(self):
        return hash(self.name)
