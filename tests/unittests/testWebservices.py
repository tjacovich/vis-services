from flask.ext.testing import TestCase
import app

class TestWebservices(TestCase):

    def create_app(self):
        """
        Create the wsgi application
        """
        app_ = app.create_app()
        return app_

    def test_resources_route(self):
            """
            Tests for the existence of a /resources route, and that it returns
            properly formatted JSON data
            """

            r = self.client.get('/resources')
            self.assertEqual(r.status_code, 200)

            # Assert each key is a string-type
            [
                self.assertIsInstance(k,
                                      basestring,
                                      msg="{0} is not a string".format(k))
                for k in r.json
            ]

            for expected_field, _type in {
                'scopes': list,
                'methods': list,
                'description': basestring,
                'rate_limit': list
            }.iteritems():

                # Assert each resource is described has the expected_field
                [
                    self.assertIn(expected_field,
                                  v,
                                  msg="{0} not in {1}".format(expected_field, v))
                    for v in r.json.values()
                ]

                # Assert every expected_field has the proper type
                [
                    self.assertIsInstance(v[expected_field],
                                          _type,
                                          msg="{0} is not type {1}"
                                          .format(v[expected_field], _type))
                    for v in r.json.values()
                ]