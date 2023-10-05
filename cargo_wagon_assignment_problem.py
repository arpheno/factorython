import pulp
from pulp import lpSum


def create_cargo_wagon_assignment_problem(entities, global_input, production_sites, output):
    # Create a PuLP minimization problem
    problem = pulp.LpProblem("Assignment Problem", pulp.LpMinimize)

    # Define the number of entities and positions
    N = len(entities)
    # give me 8 entities
    assert N % 4 == 0
    assert len(entities) == N
    # get a list of all goods in the program
    goods = set()
    for entity in entities:
        goods |= entity.keys()
    # Create binary decision variables using pulp.LpVariable.dicts
    x = pulp.LpVariable.dicts("Assignment", ((entity, position) for entity in range(N) for position in range(N)), 0, 1,
                              pulp.LpBinary)
    tally = pulp.LpVariable.dicts("Tally", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                  pulp.LpContinuous)
    flows = pulp.LpVariable.dicts("Flow", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                  pulp.LpContinuous)
    inv = pulp.LpVariable.dicts("inv", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                pulp.LpContinuous)
    penalty = pulp.LpVariable.dicts("penalty", ((group, good) for group in range(N // 4) for good in goods), 0, None,
                                    pulp.LpContinuous)
    # Constraints:
    # 1. Each entity is assigned to exactly one position
    for entity in range(N):
        problem += pulp.lpSum(x[(entity, position)] for position in range(N)) == 1

    # 2. Each position is assigned to exactly one entity
    for position in range(N):
        problem += pulp.lpSum(x[(entity, position)] for entity in range(N)) == 1
    for good in goods:
        tally[-1, good] = global_input.get(good, 0)
    groups = []
    for group_start in range(0, N, 4):
        groups.append(
            {(entity, position): x[(entity, position)] for entity in range(N) for position in
             range(group_start, group_start + 4)
             }
        )
        for good in goods:
            problem += flows[0, good] == tally[-1, good]
            flows[len(groups), good] =0
        for g, group in enumerate(groups):
            for good in goods:
                # Sum up the contributions of all chosen entities in the group
                if not good == output:
                    problem += tally[g, good] == lpSum(
                        [assignment_var * entities[entity].get(good, 0) for (entity, position), assignment_var in
                         group.items()])
                    problem += inv[g, good] == (tally[g, good] + flows[g, good] - flows[g+1,good])
                    problem += inv[g, good] >= -penalty[g, good]
    # Objective: Minimize flows
    problem += lpSum(flows.values()) + lpSum(penalty.values()) * 10000000
    # Solve the problem
    problem.solve(pulp.PULP_CBC_CMD(mip=True, maxSeconds=10))

    # Check the status of the solution
    result = []
    if pulp.LpStatus[problem.status] == 'Optimal':
        # Print the solution
        for position in range(N):
            for entity in range(N):
                if pulp.value(x[(entity, position)]) == 1:
                    result.append(production_sites[entity])
                    # print(f"Entity {entity} is assigned to Position {position}")
        flows = {key: pulp.value(value) for key, value in flows.items()}
        # group the flows by group
        flows = {key[0]: {key[1]: value for key, value in flows.items() if key[0] == key[0]} for key in flows.keys()}
        return result, flows
    else:
        raise Exception("No optimal solution found.")


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
    global_input = {'copper-plate': 0, 'iron-plate': 0, 'copper-cable': 0, 'electronic-circuit': 30, 'stone-tablet': 0}
    create_cargo_wagon_assignment_problem(entities, global_input, output='iron-plate')
