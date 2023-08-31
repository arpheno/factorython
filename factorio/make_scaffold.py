import json

import clipboard

from factorio.factorio_loader import load_factorio
from factorio.schema.model import Model

text = clipboard.paste()
blueprint = Model(**json.loads(load_factorio(text)))
blueprint.blueprint.scaffold()

clipboard.copy(blueprint.to_factorio())
