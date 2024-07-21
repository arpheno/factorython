from itertools import product
from pprint import pprint

import pulp
from pulp import lpSum


class CargoWagonAssignmentProblem:
    def __init__(self, mip=True, time_limit=30, **solver_kwargs):
        self.mip = mip
        self.time_limit = time_limit
        self.solver_kwargs = solver_kwargs

    def __call__(self, entities, global_input, production_sites, outputs):
        # Create a PuLP minimization problem
        problem = pulp.LpProblem("Assignment Problem", pulp.LpMinimize)

        # Define the number of entities and positions
        N = len(entities)
        # give me 8 entities
        try:
            assert N % 4 == 0
        except AssertionError as e:
            raise e
        assert len(entities) == N
        # get a list of all goods in the program
        goods = set()
        for entity in entities:
            goods |= entity.keys()
        for output in outputs:
            goods.remove(output)
        # Create binary decision variables using pulp.LpVariable.dicts
        x = pulp.LpVariable.dicts("Assignment", ((entity, position) for entity in range(N) for position in range(N)), 0,
                                  1,
                                  pulp.LpBinary)
        tally = pulp.LpVariable.dicts("Tally", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                      pulp.LpContinuous)
        flows = pulp.LpVariable.dicts("Flow", ((group, good) for group in range(N // 4 + 1) for good in goods), None,
                                      None,
                                      pulp.LpContinuous)
        unique_flows = pulp.LpVariable.dicts("unique_flow",
                                             ((group, good) for group in range(N // 4 + 1) for good in goods),
                                             cat=pulp.LpBinary)
        inv = pulp.LpVariable.dicts("inv", ((group, good) for group in range(N // 4) for good in goods), None, None,
                                    pulp.LpContinuous)
        penalty = pulp.LpVariable.dicts("penalty", ((group, good) for group in range(N // 4) for good in goods), 0,
                                        None,
                                        pulp.LpContinuous)
        # Constraints:
        # 1. Each entity is assigned to exactly one position
        for entity in range(N):
            problem += pulp.lpSum(x[(entity, position)] for position in range(N)) == 1

        # 2. Each position is assigned to exactly one entity
        for position in range(N):
            problem += pulp.lpSum(x[(entity, position)] for entity in range(N)) == 1

        groups = []
        for group_start in range(0, N, 4):
            groups.append(
                {(entity, position): x[(entity, position)] for entity in range(N) for position in
                 range(group_start, group_start + 4)
                 }
            )
        for good in goods:
            problem += flows[0, good] <= global_input.get(good, 0)
            problem += flows[len(groups), good] >= 0

        for g, group in enumerate(groups):
            for good in goods:
                # Sum up the contributions of all chosen entities in the group
                problem += tally[g, good] == lpSum(
                    [assignment_var * entities[entity].get(good, 0)
                     for (entity, position), assignment_var in
                     group.items()])

                # The inventory of the group is the sum of the tally and the flows
                problem += inv[g, good] == (tally[g, good] + flows[g, good] - flows[g + 1, good])

                # The flows should be positive, so we add a penalty for negative flows
                problem += inv[g, good] >= -penalty[g, good]
                problem += flows[g, good] >= 0
                problem += unique_flows[g, good] * 100000000 >= flows[g, good]

        # Objective: Minimize penalty
        flow_weighting = {'petroleum-gas': 0, 'water': 0, 'sulfuric-acid': 0, 'lubricant': 0,
                          'automation-science-pack': 0.001, 'chemical-science-pack': 0.001,
                          'logistic-science-pack': 0.001}
        flow_contribution = lpSum(flows[g, good] * flow_weighting.get(good, 1) for g, good in flows.keys())
        # flow_contribution=lpSum(flows.values())
        problem += flow_contribution + lpSum(penalty.values()) * 10_000_000

        # Solve the problem
        problem.solve(pulp.PULP_CBC_CMD(mip=self.mip, timeLimit=self.time_limit, **self.solver_kwargs))

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
            flows = [{good: flows[g, good] for good in goods} for g in range(len(groups))]
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
