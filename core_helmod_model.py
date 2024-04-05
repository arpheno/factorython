from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus


def build_core_model(recipe_df, production_rates):
    problem = LpProblem("ProductionLineProblem", LpMinimize)
    recipes = list(recipe_df.columns)
    building_count = LpVariable.dicts(
        "building_count", recipe_df.columns, lowBound=0, cat="Continuous"
    )
    net_production = LpVariable.dicts(
        "net_production", recipe_df.index, lowBound=0, cat="Continuous"
    )

    # Define constraints
    recipe_dict = recipe_df.to_dict()
    for item in recipe_df.index:
        p = lpSum(
            [
                recipe_dict[transformation][item]
                * building_count[transformation]
                * production_rates.get(transformation, 1)
                for transformation in recipes
                # if recipe_dict[transformation][item] > 0
            ]
        )
        problem += net_production[item] == p

    # Forbid production of trash
    for item in {"se-broken-data", "se-contaminated-scrap","se-scrap",'landfill','copper-ore','iron-ore','heavy-oil'}:
        problem += net_production[item] == 0

    problem.net_production = net_production
    problem.building_count = building_count
    problem.recipes = recipes
    return problem


def solve_model(problem):
    problem.solve()
    status = LpStatus[problem.status]
    return status, problem.building_count, problem.net_production
