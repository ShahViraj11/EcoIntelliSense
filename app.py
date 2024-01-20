import json
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for

import apikeys


app = Flask(__name__)
app.secret_key = apikeys.autho_client_secret
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=apikeys.autho_client_id,
    client_secret=apikeys.autho_client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{apikeys.autho_domain}/.well-known/openid-configuration',
)

@app.route('/')
def hello():
    return render_template('index (1).html')

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))

if __name__ == '__main__':
    app.run()
