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
    )]
spm_recipes = [
    Recipe(name='rgspm',
           products=[Product(name='rgspm', amount=1, type='item')],
              ingredients=[Ingredient(name='logistic-science-pack' ,amount=1, type='item'),
                           Ingredient(name='automation-science-pack' ,amount=1, type='item')],
                energy=30,
           category='researching'),
    Recipe(name='rgbspm',
           products=[Product(name='rgbspm', amount=1, type='item')],
           ingredients=[Ingredient(name='logistic-science-pack' ,amount=1, type='item'),
                        Ingredient(name='automation-science-pack' ,amount=1, type='item'),
                        Ingredient(name='chemical-science-pack' ,amount=1, type='item')
                        ],
           energy=30,
           category='researching'),
    Recipe(name='rgbospm',
           products=[Product(name='rgbospm', amount=1, type='item')],
           ingredients=[Ingredient(name='logistic-science-pack', amount=1, type='item'),
                        Ingredient(name='automation-science-pack', amount=1, type='item'),
                        Ingredient(name='chemical-science-pack', amount=1, type='item'),
                        Ingredient(name='se-rocket-science-pack', amount=1, type='item'),
                        ],
           energy=30,
           category='researching'),
]
