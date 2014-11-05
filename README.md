# adsabs-webservices-blueprint

A sample Flask application for backend adsabs (micro) web services. 

### Overview

  - `wsgi.py`: WSGI entrypoint for all applications
  - `sample_application/app.py`:  Application boostrapping code, including defining app-specific routes
  - `sample_application/config.py`: app.config; Any definitions in `local_config.py` in the same directory will overwrite.
  - `sample_application/views.py`: flask-restful based views.
  - `sample_application/client.py`: thin wrapper around requests.session; bound to app at initialization. Useful for applications that require sending e.g. oauth2 tokens to other services
  - `sample_application/README.md`: Application specific README.md
  - `sample_application/tests/`: unittests
