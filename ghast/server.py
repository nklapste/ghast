# -*- coding: utf-8 -*-

"""Flask server definition"""

from logging import getLogger
import subprocess

from flask import Flask, request, Blueprint, url_for
from flask_restplus import Api, Resource, fields

__log__ = getLogger(__name__)

APP = Flask(__name__)

__api_version__ = (0, 0, 0)

API_BLUEPRINT = Blueprint('ghast api', __name__)

# to be set within __main__.py
ALERT_SCRIPT_PATH = None
# to be set within __main__.py
API_HTTPS = False


class HTTPSApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'https' if API_HTTPS else 'http'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


API = HTTPSApi(
    API_BLUEPRINT,
    version="{}.{}.{}".format(*__api_version__),
    title='Graylog HTTP Alert Script Triggerer (ghast) API',
    doc='/doc',
    description='API for the Graylog HTTP Alert Script Triggerer (ghast)',
    contact_email="nklapste@ualberta.ca",
)


http_alert_script_triggered_model = API.model(
    'http_alert_script_triggered',
    {
        'script': fields.String(
            description='Path to the script that was triggered as a result '
                        'of the given Graylog HTTP alert callback',
            required=False,
        ),
        'script_return_code': fields.Integer(
            description="Return code of the script that was triggered as a "
                        "result of the given Graylog HTTP alert callback",
            required=False
        )
    }
)


@API.route("/")
class AlertKickScript(Resource):
    @API.doc(False)
    def get(self):
        # removing automatic/implicit support for GET requests
        API.abort(405)

    @API.marshal_with(http_alert_script_triggered_model,
                      code=200, skip_none=True)
    def post(self):
        # TODO: validate Graylog HTTP alert callback json
        json_data = request.json

        return_code = None
        if ALERT_SCRIPT_PATH is not None:
            return_code = subprocess.call(ALERT_SCRIPT_PATH)

        return {
            "script": ALERT_SCRIPT_PATH,
            "script_return_code": return_code
        }, 200
