import base64
import json
import zlib

import clipboard

from factorio.factorio_loader import load_factorio
from factorio.schema.model import Model

text = clipboard.paste()
raw=load_factorio(text)
# blueprint.blueprint.scaffold()
raw=raw.replace(b'"curved-rail"',b'"se-space-curved-rail"')
raw=raw.replace(b'"straight-rail"',b'"se-space-straight-rail"')
factorio_blueprint = '0' + base64.b64encode(zlib.compress(raw)).decode('utf-8')

clipboard.copy(factorio_blueprint)
