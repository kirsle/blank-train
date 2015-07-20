# The [\_\_\_\_] Train

The train organizer app for June 2015 ZEFR Hackathon. It's pronounced
"The [Blank] Train", or "The [\_\_\_\_] Train"

# Introduction

In our engineering Slack chat, we would organize "trains" such as "lunch train"
or "Another Kind of Sunrise train" in channels like `#lunch` or `#fun-engineering`, but
occasionally people would get left out for not paying attention to the chat
or whatever.

![sad](https://raw.githubusercontent.com/ZEFR-INC/blank-train/master/screenshot/sad.png)

So, enter **The [\_\_\_\_] Train**! It provides a central place to organize trains, join/leave them and see who's all on board so nobody gets left out. It also posts notifications to Slack when a train is created and sends a reminder when it's about to leave.

![Blank Train](https://raw.githubusercontent.com/ZEFR-INC/blank-train/master/screenshot/slack.png)

# Setup

Python: `pip install -r requirements.txt`

Node: `bower install`

Test with `python runserver.py`; use `app.wsgi` with Apache2 + `mod_wsgi`.

# Configuration

Make a file named `settings.yml` that overrides options in `defaults.yml`. Important keys:

* `mail`: Settings for e-mail server. Installing a local `sendmail` and leaving these as defaults should work in most cases.
* `slack_hook`: The incoming Slack hook URL for posting messages to a channel.
* `slack_channel`: Name of the channel on Slack to post to.
* `login_methods`: Configure methods for logging into your app. Supported methods are "password" (users register their own email and password), and "cas" (use a Central Authentication Service, v1 API only). Set a `true` or `false` value for these methods accordingly.
* `cas_url`: If you use CAS v1 to log in, this is the base URL for it.

