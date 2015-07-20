#!/usr/bin/env python
from __future__ import unicode_literals, absolute_import

from flask import Flask, g, session, render_template
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import timedelta

from train.blueprints.account import mod as account_bp
from train.blueprints.train import mod as train_bp
from train.models import User, engine
from train.settings import get_config

def create_app():
    app = Flask(__name__)
    c = get_config()

    app.config["SECRET_KEY"] = c.secrets.session_key
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)

    app.jinja_env.block_start_string    = "[%"
    app.jinja_env.block_end_string      = "%]"
    app.jinja_env.variable_start_string = "[["
    app.jinja_env.variable_end_string   = "]]"
    app.jinja_env.comment_start_string  = "[#"
    app.jinja_env.comment_end_string    = "#]"

    app.jinja_env.block_start_string    = "[%"
    app.jinja_env.block_end_string      = "%]"
    app.jinja_env.variable_start_string = "[["
    app.jinja_env.variable_end_string   = "]]"
    app.jinja_env.comment_start_string  = "[#"
    app.jinja_env.comment_end_string    = "#]"

    @app.before_request
    def before_request():
        g.db = scoped_session(sessionmaker(autocommit=False,
                                           autoflush=False,
                                           bind=engine))
        g.user = None
        if "auth" in session and session["auth"]:
            user = g.db.query(User).get(session["user_id"])
            g.user = user

        session.permanent = True

    @app.teardown_appcontext
    def after_request(exception=None):
        g.db.remove()

    @app.route("/")
    def index():
        user = None
        if g.user:
            user = g.user.serialize
        return render_template("index.html",
            user=user,
            config=c,
            title=c.app_title,
            logo=c.logo_url,
        )

    app.register_blueprint(account_bp, url_prefix="/v1/account")
    app.register_blueprint(train_bp, url_prefix="/v1/train")

    return app
