import json
import os


def get_secret():
    return json.loads(os.environ.get('SECRETS'))
