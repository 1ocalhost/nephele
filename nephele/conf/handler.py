from flask import request
import json
import base64
from nephele.utils import Nephele

nephele = Nephele(__file__)


def encode_conf(obj):
    data = json.dumps(obj).encode()
    result = base64.urlsafe_b64encode(data)
    return result.decode().replace('=', '')


def decode_conf(data):
    try:
        text = base64.urlsafe_b64decode(data.decode() + '==')
        return json.dumps(json.loads(text), indent=4, ensure_ascii=False)
    except Exception:
        return 'bad data!'


def doConvert():
    data = request.get_data()
    try:
        obj = json.loads(data)
    except Exception:
        return decode_conf(data)

    return encode_conf(obj)


def handle_req():
    if request.method == 'POST':
        return doConvert()

    return nephele.read_file('ui.html')
