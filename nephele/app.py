from flask import Flask

app = Flask(__name__)


def add_handler(rule, name, **options):
    mod = __import__(f'nephele.{name}.handler')
    handler = getattr(mod, name).handler.handle_req
    app.add_url_rule(rule, name, handler, **options)


@app.route('/')
def handle_index():
    return 'hello there!'


add_handler('/conf', 'conf', methods=['GET', 'POST'])
add_handler('/feed', 'feed')


if __name__ == '__main__':
    app.run(debug=True)
