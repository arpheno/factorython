import pulp
from pulp import lpSum
def create_cargo_wagon_assignment_problem(entities):
    # Create a PuLP minimization problem
    problem = pulp.LpProblem("Assignment Problem", pulp.LpMinimize)

    # Define the number of entities and positions
    N = len(entities)
    # give me 8 entities
    assert N % 4 == 0
    assert len(entities) == N
    goods = entities[0].keys()
    global_input = {'copper-plate': 0, 'iron-plate': 0, 'copper-cable': 0, 'electronic-circuit': 30, 'stone-tablet': 0}
    # Create binary decision variables using pulp.LpVariable.dicts
    x = pulp.LpVariable.dicts("Assignment", ((entity, position) for entity in range(N) for position in range(N)), 0, 1,
                              pulp.LpBinary)
    tally = pulp.LpVariable.dicts("Tally", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                  pulp.LpContinuous)
    flows = pulp.LpVariable.dicts("Flow", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                  pulp.LpContinuous)
    # Constraints:
    # 1. Each entity is assigned to exactly one position
    for entity in range(N):
        problem += pulp.lpSum(x[(entity, position)] for position in range(N)) == 1

    # 2. Each position is assigned to exactly one entity
    for position in range(N):
        problem += pulp.lpSum(x[(entity, position)] for entity in range(N)) == 1
    for good in goods:
        tally[-1, good] = global_input[good]
    groups = []
    for group_start in range(0, N, 4):
        groups.append(
            {(entity, position): x[(entity, position)] for entity in range(N) for position in
             range(group_start, group_start + 4)
             }
        )
        for g, group in enumerate(groups):
            for good in goods:
                # First block is special and receives the global input
                problem+= flows[g, good] == tally[g-1,good]+tally[g,good]
                # Sum up the contributions of all chosen entities in the group
                problem += tally[g,good] == lpSum(
                    [assignment_var * entities[entity][good] for (entity, position), assignment_var in group.items()])
    # Objective: Minimize flows
    problem += lpSum(flows.values())
    # Solve the problem
    problem.solve()

    # Check the status of the solution
    if pulp.LpStatus[problem.status] == 'Optimal':
        # Print the solution
        for entity in range(N):
            for position in range(N):
                if pulp.value(x[(entity, position)]) == 1:
                    print(f"Entity {entity} is assigned to Position {position}")
    else:
        print("No optimal solution found.")
if __name__ == '__main__':
    entities = [
        {'iron-plate': 1, 'copper-plate': 0, 'copper-cable': 1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 0, 'copper-plate': 1, 'copper-cable': -1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 1, 'copper-plate': 0, 'copper-cable': 1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 0, 'copper-plate': 1, 'copper-cable': -1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 1, 'copper-plate': 0, 'copper-cable': 1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 0, 'copper-plate': 1, 'copper-cable': -1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 1, 'copper-plate': 0, 'copper-cable': 1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 0, 'copper-plate': 1, 'copper-cable': -1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 1, 'copper-plate': 0, 'copper-cable': 1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 0, 'copper-plate': 1, 'copper-cable': -1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 1, 'copper-plate': 0, 'copper-cable': 1, 'electronic-circuit': -1, 'stone-tablet': 0},
        {'iron-plate': 0, 'copper-plate': 1, 'copper-cable': -1, 'electronic-circuit': -1, 'stone-tablet': 0},
    ]
    create_cargo_wagon_assignment_problem(entities)
