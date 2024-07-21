from multiprocessing import Pool


def build_blueprint(args):
    mall, line = args
    return mall.construct_blueprint_string(line)


def generate_blueprints(malls, lines, production_sites, flows):
    with Pool() as pool:
        args = zip(malls, lines, production_sites, flows)
        blueprint_strings = pool.map(build_blueprint, args)

    return blueprint_strings
