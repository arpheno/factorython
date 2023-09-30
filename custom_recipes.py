from data_structures.recipe import Recipe, Product, Ingredient

probe_recipes = [
    Recipe(
        name="se-star-data",
        products=[Product(name="se-star-probe-data", amount=1000, type="item")],
        ingredients=[Ingredient(name="se-star-probe", amount=1, type="item")],
        energy=1000,
        category="se-space-probe-launch",
    ),
    Recipe(
        name="se-belt-probe-data",
        products=[Product(name="se-belt-probe-data", amount=1000, type="item")],
        ingredients=[Ingredient(name="se-belt-probe", amount=1, type="item")],
        energy=1000,
        category="se-space-probe-launch",
    ),
    Recipe(
        name="se-satellite-telemetry",
        products=[Product(name="se-satellite-telemetry", amount=100, type="item")],
        ingredients=[Ingredient(name="satellite", amount=1, type="item")],
        energy=1000,
        category="se-space-probe-launch",
    ),
]
