from __future__ import unicode_literals, absolute_import

from flask import jsonify
from itsdangerous import URLSafeSerializer

from train.settings import get_config

# HTTP status codes
OK          = 200
CREATED     = 201
BAD_REQUEST = 400
FORBIDDEN   = 403
NOT_FOUND   = 404
CONFLICT    = 409


def resp(result=None, error=None, message=None, **kwargs):
    """Send a standardized JSON response."""
    output = dict()
    if error:
        output["error"] = error
    if message:
        output["message"] = message
    if not error or message:
        output["result"] = result
    output.update(**kwargs)
    return jsonify(output)


def signed_serialize(data):
    """Serialize signed data."""
    c = get_config()
    s = URLSafeSerializer(c.secrets.signing_key)
    return s.dumps(data)


def signed_deserialize(token):
    """De-serialize signed data."""
    c = get_config()
    s = URLSafeSerializer(c.secrets.signing_key)
    try:
        result = s.loads(token)
        return result
    except:
        return None
