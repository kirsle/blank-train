from __future__ import unicode_literals, absolute_import

import json
import requests

from train.settings import get_config

def post_message(message, usernames=None):
    c = get_config()

    if usernames is None:
        message = "<!channel>: {}".format(message)
    else:
        for user in usernames:
            message = "<@{}> ".format(user) + message

    requests.post(c.slack_hook,
        headers={"Content-Type": "application/json"},
        data=json.dumps(dict(
            text=message,
            channel=c.slack_channel,
            username="blank-train",
            icon_emoji=":train:"
        )))

def list_users():
    c = get_config()
    if c.slack_token == "x":
        return dict(ok=False, error="Missing Slack API token")

    r = requests.get("https://slack.com/api/users.list",
        params=dict(token=c.slack_token))
    return r.json()
