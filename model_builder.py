from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus


def optimize_transformations(df, production_rates, product, min_quantity):
    # Create a PuLP linear programming problem
    problem = LpProblem("Transformation Optimization", LpMinimize)

    # Define decision variables
    transformations = list(df.columns)
    items = df.index
    quantities = LpVariable.dicts("quantity", transformations, lowBound=0, cat="Continuous")
    production_exprs = LpVariable.dicts("production_expr",items,lowBound=0, cat="Continuous")

    #Objective
    objective_terms = [quantities[transformation] for transformation in transformations]
    problem += lpSum(objective_terms)
    # Define constraints
    for item in df.index:
        problem+= production_exprs[item] == lpSum(
            [df.loc[item, transformation] * quantities[transformation] * production_rates.get(transformation,1) for
             transformation in transformations])
        if item == product:
            problem += production_exprs[item] >= min_quantity
        if item in {'se-broken-data','se-contaminated-scrap'}:
            problem += production_exprs[item] ==0

    # Solve the problem
    problem.solve()

    # Retrieve the results
    status = LpStatus[problem.status]
    optimal_quantities = {transformation: quantities[transformation].varValue for transformation in transformations}
    return status, optimal_quantities,  production_exprs
