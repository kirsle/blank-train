#!/usr/bin/env python

"""Watcher script for the train leaving the station."""

import sys
import os
import argparse
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker, scoped_session
import re

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from train.models import engine, Train
from train.slack import post_message, list_users

users_cache = None
users_cache_expire = 0

def main():
    db = connect()

    # Keep a cache of recently notified trains.
    recent_notify = dict()

    while True:
        time.sleep(5)

        # Trains leaving within 2 minutes
        two_mins = datetime.utcnow() + timedelta(minutes=2)
        for train in db.query(Train).filter(Train.expires >= datetime.utcnow())\
                                    .filter(Train.expires <= two_mins)\
                                    .all():
            if train.id in recent_notify:
                continue

            print "Notify Slack: train {} is leaving soon".format(train.name)
            train_name = train.name
            if not train_name.lower().endswith("train"):
                train_name += " Train"

            # Get Slack names to ping.
            users = get_users([m.username for m in train.passengers])

            # Notify Slack
            post_message("*All aboooaaarrrd!* :train2:\n\n"
                "The *{name}* is leaving within 2 minutes! *Choo Choo!* "
                ":train: :dash: :dash:".format(
                name=train_name
                ), users)

            # Cache it so we don't notify twice within about 5 minutes
            recent_notify[train.id] = time.time()

        # Clear the cache of recent trains.
        for train_id, last_notify in recent_notify.items():
            if time.time() - last_notify > (5*60):
                del recent_notify[train_id]
                continue

def get_users(emails):
    """Retrieve the Slack usernames for the given emails.

    Returns an array of Slack user IDs and user names, for use in Slack bot
    messages. They're in the format '<@U1234|name>' - if the `name` part has
    any special characters, they're stripped off.

    It does it this way because '<@username>' works to send an at-notification
    for most users, but not if the user has dots in their name. Doing something
    like <@U1234|dot.name> also fails because of the dot. It seems that when
    given this syntax, Slack only cares about the user ID part, so for
    troublesome names we'll just strip punctuation."""
    global users_cache
    global users_cache_expire

    users = users_cache
    if users is None or time.time() > users_cache_expire:
        users_cache = list_users()
        users_cache_expire = time.time()
        users = users_cache

    if not "members" in users:
        return None

    usernames = set()
    for u in users["members"]:
        if not "email" in u["profile"]:
            print "No email for user", u.get("name")
            continue
        if u["profile"]["email"] in emails:
            name = re.sub(r'[^A-Za-z0-9]', '', u["name"])
            usernames.add("{}|{}".format(u["id"], name))

    usernames = list(usernames)
    if len(usernames) == 0:
        return None
    return usernames


def connect():
    return scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Watcher")
    parser.add_argument(
        "--port", "-p",
        type=int,
        help="Port to listen on",
        default=2006,
    )
    args = parser.parse_args()

    main()
