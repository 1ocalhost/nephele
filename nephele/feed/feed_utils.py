import json
import base64
from urllib.parse import urlparse, parse_qs, urlencode
from functools import partial
from nephele.utils import AttrDict, APP_NAME

GROUP_NAME = APP_NAME.capitalize()


def b64_decode(data):
    if data is None:
        return None

    d = data.replace('_', '/').replace('-', '+')
    try:
        return base64.b64decode(d.strip() + '==').decode()
    except Exception:
        return


def b64_encode(data, url_safe=False, padding=True):
    if isinstance(data, str):
        data = data.encode()

    if url_safe:
        encoder = base64.urlsafe_b64encode
    else:
        encoder = base64.b64encode

    result = encoder(data).decode()
    if not padding:
        result = result.replace('=', '')

    return result


class SsrUrl:
    PACKED_QUERY = ['remarks', 'group']

    def __init__(self, url):
        self.decode(url)

    def decode(self, url):
        sep = url.find('/?')
        self.host_str = url[:sep]
        self.query_str = url[sep:]
        self.query = self.parse_query()
        self.unpack_query()

    def parse_query(self):
        url = urlparse(self.query_str)
        query = parse_qs(url.query, keep_blank_values=True)
        result = map(lambda x: (x[0], x[1][0]), query.items())
        return dict(result)

    def unpack_query(self):
        for name in self.PACKED_QUERY:
            self.query[name] = b64_decode(self.query[name])

    def encode(self):
        query = dict(self.query)
        for name in self.PACKED_QUERY:
            query[name] = b64_encode(
                query[name], url_safe=True, padding=False)
        return self.host_str + '/?' + urlencode(query)

    @classmethod
    def loads(cls, url):
        return cls(url)

    @classmethod
    def dumps(cls, url):
        return url.encode()


class VmessQuan:
    @classmethod
    def cvt_obfs_param(cls, p):
        k, v = p
        if not isinstance(v, str):
            v = json.dumps(v)
        return f'{k}={v}'

    @classmethod
    def build_obfs_params(cls, v, o):
        if v.net == 'ws':
            obfs = 'ws'
        else:
            obfs = 'http'

        obfs_path = (v.path or '/')
        obfs_host = (v.host or v.add)
        obfs_header = f'Host: {obfs_host}[Rr][Nn]' \
            f'User-Agent: {o.user_agent}'

        return {
            'obfs': obfs,
            'obfs-path': f'"{obfs_path}"',
            'obfs-header': f'"{obfs_header}"',
        }

    @classmethod
    def encode(cls, vmess_conf, options):
        v, o = AttrDict(vmess_conf), options
        quan_params = {
            'group': o.group,
            'over-tls': (v.tls == 'tls'),
            'certificate': 1,
        }

        if v.net == 'ws' or v.type != 'none':
            obfs_params = cls.build_obfs_params(v, o)
            quan_params.update(**obfs_params)

        all_parts = [
            f'{v.ps} = vmess',
            v.add,
            v.port,
            o.cipher,
            f'"{v.id}"',
        ]

        all_parts += map(cls.cvt_obfs_param, quan_params.items())
        return ', '.join(map(str, all_parts))


def block_to_list(block):
    result = b64_decode(block).split('\n')
    return list(filter(len, result))


def list_to_block(list_):
    list_ = list(list_)
    return b64_encode('\n'.join(list_))


def decode_uri(options, uri):
    scheme, data = uri.split('://')
    data = b64_decode(data)
    if data is None:
        return

    decoder = encoding_provider(options, scheme)[0]
    return scheme, decoder(data)


def encode_uri(options, item):
    scheme, obj = item
    encoder = encoding_provider(options, scheme)[1]
    data = encoder(obj)
    return scheme + '://' + b64_encode(data)


def encoding_provider(options, scheme):
    def vmess_quan_encode(conf):
        return VmessQuan.encode(conf, options)

    if scheme == 'vmess' and options.get('variant') == 'quan':
        scheme = 'vmess-quan'

    return {
        'vmess': [json.loads, json.dumps],
        'vmess-quan': [json.loads, vmess_quan_encode],
        'ssr': [SsrUrl.loads, SsrUrl.dumps],
    }[scheme]


def filter_feed(feed, filter_, options):
    servers = block_to_list(feed)
    servers = map(partial(decode_uri, options), servers)
    servers = [s for s in servers if s and filter_(s)]
    servers = map(partial(encode_uri, options), servers)
    return list_to_block(servers)


def filter_by_words(feed, words, options={}):
    options = AttrDict(options)

    def filter_(server):
        scheme, obj = server
        if scheme == 'vmess':
            label = obj['ps']
        elif scheme == 'ssr':
            label = obj.query['remarks']
            obj.query['group'] = GROUP_NAME

        for word in words:
            if word in label:
                return False
        return True

    return filter_feed(feed, filter_, options)


def list_feed(feed):
    def filter_(server):
        scheme, obj = server
        if scheme == 'vmess':
            print(obj['ps'])
        elif scheme == 'ssr':
            print(obj.query)

    filter_feed(feed, filter_)


def test():
    with open('ssr.txt') as f:
        feed = f.read()

    list_feed(feed)
    print('-' * 20)
    list_feed(filter_by_words(feed, ['IPLC']))


if __name__ == '__main__':
    test()
