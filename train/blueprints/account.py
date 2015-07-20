from __future__ import unicode_literals, absolute_import

"""Endpoints for account management."""

from flask import Blueprint, g, redirect, url_for, session, render_template
from webargs import Arg
from webargs.flaskparser import use_kwargs
import bcrypt
import requests
from functools import wraps

from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from train.utils import (OK, BAD_REQUEST, CREATED, CONFLICT, FORBIDDEN,
    NOT_FOUND, resp, signed_serialize, signed_deserialize)
from train.settings import get_config
from train.models import User

mod = Blueprint("account", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "auth" in session and session["auth"]:
            return f(*args, **kwargs)
        else:
            return resp(error="Auth required.")
    return decorated_function

@mod.route("/login", methods=["POST"])
@use_kwargs({
    "username": Arg(unicode, required=True, use=lambda s: s.lower()),
    "password": Arg(unicode, required=True),
})
def login(username, password):
    """Log into the app."""

    user = g.db.query(User).filter(User.username == username).first()
    if not user:
        return resp(error="User name not found."), NOT_FOUND
    if not user.verified:
        return resp(error="This account is not verified. Check your email "
            "for the verification link and try again."), FORBIDDEN

    if not check_pass(password, user.password):
        return resp(error="Bad password."), FORBIDDEN

    session["auth"] = True
    session["user_id"] = user.id
    return resp(message="Welcome back."), OK


@mod.route("/cas_login", methods=["GET"])
def cas_login():
    c = get_config()
    service = url_for(".cas_callback", _external=True)
    return redirect(c.cas_url + "/login?service=" + service)


@mod.route("/cas_callback", methods=["GET"])
@use_kwargs({
    "ticket": Arg(unicode, required=True),
})
def cas_callback(ticket):
    c = get_config()
    r = requests.get(c.cas_url + "/validate",
        params=dict(
            ticket=ticket,
            service=url_for(".cas_callback", _external=True),
        ))
    resp_values = r.text.split()
    if len(resp_values) == 2:
        is_valid, username = resp_values
        username = username.lower()

        if is_valid == "yes":
            # Auth successful!
            if not domain_allowed(username):
                return render_template("error.html",
                    error="{} Accounts Only!".format(
                        c.registration.email_domain
                    ))

            user = g.db.query(User).filter(User.username == username).first()
            if not user:
                user = User(username=username, password="!", verified=True)
                g.db.add(user)
                g.db.commit()

            session["auth"] = True
            session["user_id"] = user.id
            return redirect(url_for("index"))
    return render_template("error.html", error="Authentication error.")


@mod.route("/logout", methods=["GET"])
def logout():
    """Sign out."""
    session.pop("auth", None)
    session.pop("user_id", None)
    return resp(message="Bye."), OK


@mod.route("/register", methods=["POST"])
@use_kwargs({
    "username": Arg(unicode, required=True, use=lambda s: s.lower()),
    "password": Arg(unicode, required=True),
})
def register(username, password):
    """Register an account."""
    c = get_config()

    # Limit accounts by email?
    if not domain_allowed(username):
        return resp(error="{} accounts only!".format(
            c.registration.email_domain
        )), BAD_REQUEST

    # Conflict?
    user = g.db.query(User).filter(User.username == username).first()
    if user and user.verified:
        return resp(error="User already exists."), CONFLICT

    # Make their account.
    if not user:
        user = User(username=username, password=hash_pass(password))
        g.db.add(user)
        g.db.commit()

    # Serialize the activation token.
    token = signed_serialize({"t": "activate", "u": user.id})
    print "Activation token:", token

    # Email them the token.
    try:
        send_email(username, token)
    except Exception as e:
        print "Couldn't send mail!", e

    return resp(message="Account created. Check your email for "
        "activation link."), CREATED


@mod.route("/verify", methods=["GET"])
@use_kwargs({
    "token": Arg(unicode, required=True)
})
def verify(token):
    """Verify an account."""
    decode = signed_deserialize(token)
    if not decode or decode["t"] != "activate":
        return render_template("error.html",
            error="Invalid registration token.",
        ), FORBIDDEN

    # Get the account.
    user = g.db.query(User).get(decode["u"])
    if not user:
        return render_template("error.html",
            error="User ID not found.",
        ), NOT_FOUND

    # Activate them.
    user.verified = True
    g.db.commit()
    return render_template("verified.html"), OK


def domain_allowed(email):
    """Check if the email is allowed to register."""
    c = get_config()
    if c.registration.limit_domains:
        if not email.lower().endswith(c.registration.email_domain):
            return False
    return True


def hash_pass(passwd):
    """Hash the password."""
    c = get_config()
    return bcrypt.hashpw(str(passwd).encode("utf-8"),
        bcrypt.gensalt(int(c.bcrypt.iterations))).decode("utf-8")


def check_pass(given, correct):
    """Verify the password."""
    test = bcrypt.hashpw(str(given).encode("utf-8"),
        str(correct).encode("utf-8")).decode("utf-8")
    return correct == test


def send_email(address, token):
    """Send the verification e-mail."""
    c = get_config()
    link = url_for(".verify", token=token, _external=True)

    # Prepare the e-mail message.
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your account for the [____] Train"
    msg["From"] = "[____] Train <{}>".format(c.mail.sender)
    msg["To"] = address

    html = render_template("activate_email.html", link=link)
    text = text_verify(link)
    part1 = MIMEText(text.encode("UTF-8"), "plain", "UTF-8")
    part2 = MIMEText(html.encode("UTF-8"), "html", "UTF-8")

    # Attach
    msg.attach(part1)
    msg.attach(part2)

    # Send email
    smtp = None
    if c.mail.ssl:
        smtp = SMTP_SSL(c.mail.host)
    else:
        smtp = SMTP(c.mail.host)

    if c.mail.username and c.mail.password:
        smtp.login(c.mail.username, c.mail.password)

    smtp.sendmail(msg["From"], address, msg.as_string())
    smtp.quit()


def text_verify(link):
    """Plain text version of e-mail."""
    return """Verify your account for the [_____] Train

Visit this URL below to verify your account:

{link}""".format(link=link)
