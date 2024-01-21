import json
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for, request
import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query
import backendfunctions


google_maps_api_key = 'AIzaSyDu9WmzWfQnxsqJhWLE8CTMlSYB0VRUrkg'

redis_password = 'EgORtEAym4obVur32FdT5qnBwi6QKAsK'

autho_domain = 'dev-oye6y425565bfb2p.us.auth0.com'
autho_client_id = 'JOsSt09A4sbeFTqq1U6DVIw6eRdyDbIp'
autho_client_secret = '3ONItRFS8Wf9w_w2_Nzu2H5zGNWelMz6E9ci1v_zw-srCFgbOcobWP_l8GGoEA26'

onebuild_api = '1build_ext.zo7ujfZa.e4ttcYOIKFi6Sy7t2FBLQy0F7L0ZrKrU'

r = redis.StrictRedis(
  host='redis-19241.c1.us-central1-2.gce.cloud.redislabs.com',
  port=19241,
  password=redis_password,)

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
app.secret_key = autho_client_secret
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=autho_client_id,
    client_secret=autho_client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{autho_domain}/.well-known/openid-configuration',
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
    print(user_projects) 
    return render_template('currentprojects.html',
                    data_list = user_projects)

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
        + autho_domain
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("hello", _external=True),
                "client_id": autho_client_id,
            },
            quote_via=quote_plus,
        )
    )
    
@app.route('/submit', methods=['GET','POST'])
def submit():
    if request.method == "POST":
        request.form
        project_name = request.form.get('projectname')
        project_street_location = request.form.get('projectlocation')
        project_coordinates = backendfunctions.geocode_address(project_street_location, google_maps_api_key)
        project_size = request.form.get('projectsize')
        add_project(session.get("user")["userinfo"]["email"], project_name, {'project_street': project_street_location,
                                                                             'project_coordinates': project_coordinates,
                                                                             'project_size': project_size})
        return redirect(url_for('report', curr_proj=str(project_name)))
        
@app.route('/report', methods=['GET','POST'])
def report():
    proj_name = request.args.get('curr_proj')  
    db_data = get_project_info(session.get("user")["userinfo"]["email"], proj_name)
    
    data = dict()
    data['name'] = proj_name
    data['location'] = db_data['project_street']
    data['coordinates'] = db_data['project_coordinates']
    temp, data['wind'] = backendfunctions.average_temp_and_wind(db_data['project_coordinates'][0], db_data['project_coordinates'][1])
    data['near_water'] = backendfunctions.water_check(db_data['project_coordinates'][0], db_data['project_coordinates'][1])
    data['labor_cost'] = backendfunctions.query_1build_construction_costs(db_data['project_coordinates'][0], db_data['project_coordinates'][1])               
    data['area'] = db_data['project_size']
    data['elevation'] = round(backendfunctions.check_mountainous_region(db_data['project_coordinates'][0], db_data['project_coordinates'][1]),2)
    data['solar'] = backendfunctions.solar_data(db_data['project_coordinates'][0], db_data['project_coordinates'][1])
    data['sustainability_scale'] = backendfunctions.sustainability_score(db_data['project_coordinates'][0], db_data['project_coordinates'][1])
    pollution_data = backendfunctions.pollution_data(db_data['project_coordinates'][0], db_data['project_coordinates'][1])
    sum = 0
    for i in range(len(pollution_data)):
        sum += pollution_data[i]['hoursInfo'][0]['indexes'][0]['aqi']
    data['air_quality_index'] = round(sum/len(pollution_data),2)
    
    print(data['wind'])
    
    return render_template('ReportDraft.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
