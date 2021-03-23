'''
conf:
{
    "feeds": ["<url>"],
    "words": ["IPLC"],
    "code": {
        "admin": ["admin"],
        "guest": ["guest"]
    }
}
'''

import requests
from flask import request
from nephele.utils import Nephele
from .feed_utils import GROUP_NAME, filter_by_words

nephele = Nephele(__file__)


def check_if_quan():
    ua = request.headers.get('user-agent')
    type_ = request.args.get('type')
    if type_ == 'quan':
        return ua

    if 'quantumult' in ua.lower():
        return ua


def make_options():
    ua = check_if_quan()
    if ua:
        return {
            'variant': 'quan',
            'cipher': 'chacha20-ietf-poly1305',
            'group': GROUP_NAME,
            'user_agent': ua,
        }
    return {}


def handle_req():
    '''
        @code: str
        @index: int=0
        @op: in ['list']
        @type: in ['quan']
    '''
    args = request.args
    conf = nephele.get_conf()
    code = args.get('code')
    if code in conf['code']['admin']:
        words = []
    elif code in conf['code']['guest']:
        words = conf['words']
    else:
        return 'bad code!'

    feeds = conf['feeds']
    if args.get('op') == 'list':
        return nephele.json(feeds)

    index = int(args.get('index', 0))
    feed_text = requests.get(feeds[index]).text

    options = make_options()
    return filter_by_words(feed_text, words, options)
