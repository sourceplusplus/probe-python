import os

from flask import Flask

from sourceplusplus.SourcePlusPlus import SourcePlusPlus

app = Flask(__name__)


def fun():
    x = 5
    y = x
    print("fun")


@app.route('/')
def hello():
    provider = str(os.environ.get('PROVIDER', 'world'))
    return 'Hello ' + provider + '!'


if __name__ == '__main__':
    SourcePlusPlus().attach()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
