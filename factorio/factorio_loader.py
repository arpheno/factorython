import base64
import zlib


def load_factorio(encoded_string):
    return zlib.decompress(base64.b64decode(encoded_string[1:]))
def dump_factorio(text):
    factorio_blueprint = '0' + base64.b64encode(zlib.compress(text)).decode('utf-8')
    return factorio_blueprint