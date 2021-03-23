import sys
from pathlib import Path

app_path = Path(__file__).absolute().parent.parent
sys.path.append(str(app_path))
from nephele.app import app  # noqa

if __name__ == '__main__':
    app.run(debug=True)
