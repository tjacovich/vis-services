import os
from flask import Blueprint, Flask
from flask import Flask, g
from views import blueprint, WordCloud, AuthorNetwork
from flask.ext.restful import Api
from client import Client
<<<<<<< HEAD


=======
>>>>>>> added tests but they dont work yet because of an unsolved error

def create_app():
  api = Api(blueprint)
  api.add_resource(WordCloud, '/word-cloud')
  api.add_resource(AuthorNetwork, '/author-network')

  app = Flask(__name__, static_folder=None) 
  app.url_map.strict_slashes = False
  app.config.from_pyfile('config')
  try:
    app.config.from_pyfile('local_config')
  except IOError:
    pass
  app.register_blueprint(blueprint)
  api.init_app(app)
  app.client = Client(app.config['CLIENT'])
  return app


if __name__ == '__main__':
  app = create_app()
  app.run(debug=True)