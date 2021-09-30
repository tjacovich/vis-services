from adsmutils import ADSFlask
from .views import WordCloud
from .views import AuthorNetwork
from .views import PaperNetwork
from flask_restful import Api
from flask_discoverer import Discoverer
from werkzeug.serving import run_simple


def create_app(**config):
    """Application factory"""

    app = ADSFlask(__name__, static_folder=None, local_config=config or {})

    app.url_map.strict_slashes = False

    api = Api(app)

    api.add_resource(WordCloud, '/word-cloud')
    api.add_resource(AuthorNetwork, '/author-network')
    api.add_resource(PaperNetwork, '/paper-network')
    
    discoverer = Discoverer(app)

    return app

if __name__ == "__main__":
    run_simple('0.0.0.0', 5555, create_app(), use_reloader=False, use_debugger=False)

