import os
from flask import Blueprint, Flask
from flask import Flask, g
from views import blueprint, WordCloud, AuthorNetwork, PaperNetwork, Resources
from flask.ext.restful import Api
from client import Client

def create_app():
  api = Api()
  api.add_resource(Resources, '/resources')
  api.add_resource(WordCloud, '/word-cloud')
  api.add_resource(AuthorNetwork, '/author-network')
  api.add_resource(PaperNetwork, '/paper-network')


  app = Flask(__name__, static_folder=None) 
  app.url_map.strict_slashes = False
  app.config.from_pyfile('config.py')
  try:
    app.config.from_pyfile('local_config.py')
  except IOError:
    pass
  app.register_blueprint(blueprint)
  api.init_app(app)
  app.client = Client(app.config['CLIENT'])
  return app
  


if __name__ == '__main__':
  app = create_app()
  app.run(debug=True)
