import os
import json
import base64
from pathlib import Path

APP_NAME = 'nephele'


def env_var(name):
    return f'{APP_NAME}_{name}'.upper()


def env_get_bool(name):
    value = os.environ.get(env_var(name))
    try:
        int_value = int(value)
        return bool(int_value)
    except ValueError:
        return bool(value)
    except Exception:
        return False


IS_DEBUG = env_get_bool('debug_mode')


def load_app_conf():
    if IS_DEBUG:
        app_path = Path(__file__).absolute().parent.parent
        with open(app_path / 'test_app_conf.json') as f:
            app_conf = f.read()
    else:
        env_name = env_var('app_conf')
        app_conf = os.environ[env_name]
        app_conf = base64.urlsafe_b64decode(app_conf + '==')

    return json.loads(app_conf)


APP_CONF = load_app_conf()


class AttrDict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Nephele:
    def __init__(self, filename):
        self.filename = Path(filename)

    def get_conf(self):
        page_name = self.filename.parent.name
        return APP_CONF[page_name]

    def read_file(self, path):
        with open(self.filename.parent / path) as f:
            return f.read(1024 * 1024 * 10)

    def json(self, obj):
        return json.dumps(obj)
