import numpy as np


def interburbul(GRIDSIZE, a, b, c, q):
    points = B = np.array([a, b, c])
    x, y = np.array([B[2] - B[0], B[1] - B[0]]) / (GRIDSIZE - 1)
    print(x, y)
    print(np.sum(np.array([x, y]).transpose() * np.array(q), axis=1) + a)
    # A*X=B
    # X = inv(a)*B


interburbul(3, [1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1])
interburbul(4, [1, 0, 0], [0, 1, 0], [0, 0, 1], [2, 1])
interburbul(5, [1, 1, 1], [0, 1, 0], [0, 0, 1], [0, 2])
interburbul(6, [-1, 0, 0], [0, 1, 0], [0, 0, 1], [3, 3])
interburbul(7, [1, 0, 0], [0, 2, 0], [0, 0, 7], [3, 1])
interburbul(8, [1, 6, 1], [8, 0, 3], [3, 9, 8], [6, 6])
interburbul(10, [0.1, 0.6, 0.1], [0.8, -0.1, 0.3], [0.3, 0.9, 0.8], [5, 2])
interburbul(15, [0.87, 0.49, 0.89], [0.48, 0.48, 0.2], [0.45, 0.86, 0.83], [14, 12])
interburbul(20, [-436,563,-811], [772,30,917], [980,576,286], [1,16])
interburbul(
    50,
    [1.618033, 0.9887498, 0.48204586],
    [2.414213, 0.562373, 0.950488],
    [3.302775, 0.6377319, 0.9464655],
    [43, 32],
)

from scipy.optimize import lsq_linear

arcospheres = ["LAMBDA", "XI", "ZETA", "THETA", "EPSILON", "PHI", "GAMMA", "OMEGA"]


def translate(f: str):
    """
    Translates a natural language arcosphere transformation to a vector:

    >>> translate('lambda omega -> xi theta')
    array([-1,  1,  0,  1,  0,  0,  0, -1])
    """
    inputs, outputs = f.split("->")
    inputs = np.array(
        [
            1 if y in [arcospheres.index(x.upper()) for x in inputs.split()] else 0
            for y in range(8)
        ]
    )
    outputs = np.array(
        [
            1 if y in [arcospheres.index(x.upper()) for x in outputs.split()] else 0
            for y in range(8)
        ]
    )
    return outputs - inputs


foldings = []
foldings.append(translate("lambda omega -> xi theta"))
foldings.append(translate("xi zeta -> theta phi"))
foldings.append(translate("xi gamma -> zeta lambda"))
foldings.append(translate("lambda theta -> epsilon zeta"))
foldings.append(translate("theta epsilon -> phi omega"))
foldings.append(translate("zeta phi -> gamma epsilon"))
foldings.append(translate("phi gamma -> omega xi"))
foldings.append(translate("epsilon omega -> lambda gamma"))
foldings.append(translate("zeta theta gamma omega -> lambda xi epsilon phi"))
foldings.append(translate("lambda xi epsilon phi -> zeta theta gamma omega"))
foldings = np.array(foldings).transpose()
print(repr(foldings))


def arcoinverse(to_invert: np.ndarray):
    solution = lsq_linear(foldings, to_invert, [0, np.inf])
    print(solution)
    if solution.status != 1:
        raise ArithmeticError
    return solution.x


if __name__ == "__main__":
    to_invert = np.array(translate("lambda zeta epsilon gamma -> xi theta phi omega"))
    solution = arcoinverse(to_invert)
    assert np.isclose(foldings @ solution - to_invert, 0).all()
    print("hurray")
    to_invert = np.array(translate("zeta theta gamma omega -> lambda xi epsilon phi"))
    solution = arcoinverse(to_invert)
    assert np.isclose(foldings @ solution - to_invert, 0).all()
    print("hurray")

    to_invert = np.array(translate(" lambda xi zeta -> theta epsilon phi"))
    solution = arcoinverse(to_invert)
    assert np.isclose(foldings @ solution - to_invert, 0).all()
    print("hurray")

    print(translate(" lambda xi zeta -> theta epsilon phi"))
