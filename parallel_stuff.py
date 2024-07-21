from multiprocessing import Pool


def build_blueprint(args):
    mall, line = args
    return mall.build_mall(line)


def generate_blueprints(malls, lines):
    blueprint_strings = []

    with Pool() as pool:
        args = zip(malls, lines)
        blueprint_strings = pool.map(build_blueprint, args)

    return blueprint_strings