from __future__ import unicode_literals, absolute_import

"""Endpoints for train management."""

from flask import Blueprint, g, url_for
from webargs import Arg
from webargs.flaskparser import use_kwargs

from datetime import datetime, timedelta

from train.utils import OK, CREATED, FORBIDDEN, NOT_FOUND, resp
from train.blueprints.account import login_required
from train.slack import post_message
from train.models import Train

mod = Blueprint("train", __name__)

@mod.route("/", methods=["GET"])
@login_required
def list_trains():
    trains = g.db.query(Train).filter(Train.expires >= datetime.utcnow()).all()
    return resp(result=[ t.serialize for t in trains ])


@mod.route("/<int:train_id>", methods=["GET"])
@login_required
def get_train(train_id):
    train = g.db.query(Train).get(train_id)
    if not train:
        return resp(error="Train not found."), NOT_FOUND
    return resp(train.serialize), OK


@mod.route("/", methods=["POST"])
@use_kwargs({
    "name": Arg(str, required=True),
    "expires": Arg(str, required=True), # expire time in seconds
})
@login_required
def make_train(name, expires):
    """Make a new train."""

    # Turn expiration into a datetime.
    expiration = datetime.strptime(expires,"%Y-%m-%dT%H:%M:%S.%fZ")

    # Make the train.
    train = Train(
        name=name,
        owner=g.user.id,
        expires=expiration,
    )
    train.passengers.append(g.user) # Creator is automatically on board
    g.db.add(train)
    g.db.commit()

    pingback = url_for("index", _external=True).strip("/") + "/#/?train={}".format(
        train.id
    )

    # Notify Slack
    train_name = name
    if not train_name.lower().endswith("train"):
        train_name += " Train"
    post_message("*A train has pulled into the station!* :train:\n\n"
        "{user} has created the *{name}*! Board the train at <{url}>\n"
        "It leaves the station in *{expires} minute{pl}*!".format(
            user=g.user.username.split("@")[0],
            name=train_name,
            url=pingback,
            expires=int((expiration - datetime.utcnow()).seconds / 60),
            pl="s" if expires != 1 else "",
        )
    )

    return resp(train.serialize), CREATED


@mod.route("/<int:train_id>", methods=["PUT"])
@use_kwargs({
    "name": Arg(unicode, required=True),
    "expires": Arg(int, required=True), # expire time in seconds
})
@login_required
def update_train(name, expires, train_id):
    """Update an existing train."""
    train = g.db.query(Train).get(train_id)
    if not train:
        return resp(error="Train not found."), NOT_FOUND

    # Turn expiration into a datetime.
    expires = datetime.utcnow() + timedelta(seconds=expires)

    train.name = name
    train.expires = expires

    g.db.commit()
    return resp(train.serialize), OK


@mod.route("/<int:train_id>", methods=["DELETE"])
@login_required
def delete_train(train_id):
    """Delete a train."""
    train = g.db.query(Train).get(train_id)
    if not train:
        return resp(error="Train not found."), NOT_FOUND

    g.db.delete(train)
    g.db.commit()
    return resp(message="Deleted."), OK


@mod.route("/<int:train_id>/join", methods=["POST"])
@login_required
def join_train(train_id):
    """Join a train."""
    train = g.db.query(Train).get(train_id)
    if not train:
        return resp(error="Train not found."), NOT_FOUND

    if datetime.utcnow() > train.expires:
        return resp(error="The train has already left the station."), FORBIDDEN

    train.passengers.append(g.user)
    g.db.commit()

    return resp(message="Joined the train."), CREATED


@mod.route("/<int:train_id>/leave", methods=["POST"])
@login_required
def leave_train(train_id):
    """Leave the train."""
    train = g.db.query(Train).get(train_id)
    if not train:
        return resp(error="Train not found."), NOT_FOUND

    train.passengers.remove(g.user)
    g.db.commit()

    return resp(message="Left the train."), OK
