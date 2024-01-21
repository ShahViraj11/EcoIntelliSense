import json
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for, request
import apikeys
import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query

from BackendFunctions import backendfunctions

r = redis.StrictRedis(
  host='redis-19241.c1.us-central1-2.gce.cloud.redislabs.com',
  port=19241,
  password=apikeys.redis_password,)

def add_project(user_id, project_name, project_info):
    # Convert project_info to JSON for storage
    project_info_json = json.dumps(project_info)

    # Set the project information in Redis
    r.hset(f'user:{user_id}:projects', project_name, project_info_json)

def get_project_info(user_id, project_name):
    # Get the project information from Redis
    project_info_json = r.hget(f'user:{user_id}:projects', project_name)

    # Convert JSON back to Python dictionary
    project_info = json.loads(project_info_json) if project_info_json else None

    return project_info

def get_project_names(user_id):
    # Get all project names for the user from Redis
    project_names = r.hkeys(f'user:{user_id}:projects')
    
    # Convert byte strings to regular strings
    project_names = [name.decode('utf-8') for name in project_names]
    
    return project_names


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
    return render_template('index (1).html',
                           session=session.get("user"), 
                           pretty=json.dumps(session.get("user"), indent=4))

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/projects")

@app.route("/projects", methods=["GET", "POST"])
def projects():
    user_projects = get_project_names(session.get("user")["userinfo"]["email"])    
    return render_template('currentprojects.html',
                    project_list = user_projects)

@app.route("/newproject", methods=["GET", "POST"])
def newproject():
    return render_template('2ndpage.html',
                    session=session.get("user"),
                    pretty=json.dumps(session.get("user"), indent=4))


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + apikeys.autho_domain
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("hello", _external=True),
                "client_id": apikeys.autho_client_id,
            },
            quote_via=quote_plus,
        )
    )
    
@app.route('/submit', methods=['GET','POST'])
def submit():
    if request.method == "POST":
        request.form
        project_name = request.form.get('projectname')
        project_location = backendfunctions.geocode_address(request.form.get('projectlocation'), apikeys.google_maps_api_key)
        project_size = request.form.get('projectsize')
        add_project(session.get("user")["userinfo"]["email"], project_name, {'project_location': project_location, 'project_size': project_size})
        return redirect(url_for('report', project_name=project_name))

@app.route('/report', methods=['GET','POST'])
def report():
    # data = get_project_info(session.get("user")["userinfo"]["email"], request.args.get('projectname'))
    data = dict()
    data['location'] = "1234 Main St, San Francisco, CA 94123"
    data['near_water'] = True
    data['completion_rate'] = 0.5
    data['labor_cost'] = 100000               
    data['area'] = 100
    data['elevation'] = 17
    data['budget_used'] = 3400
    data['extra_material_cost'] = 2100
    data['sustainability_scale'] = 64
    return render_template('ReportDraft.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
