from flask import Flask, session, abort, redirect, request, render_template, session
from google_auth_oauthlib.flow import Flow
import os
import requests
import pathlib
from pip._vendor import cachecontrol
from google.oauth2 import id_token
import google.auth.transport.requests
from flask_mysqldb import MySQL
# flask_mysqldb is used for mysql connectivity and doing queries using mysql workbench
from flask import jsonify
# jsonify library used for converting result comes from mysql queries into json format
import json
from datetime import timedelta, datetime
import requests_oauthlib
import flask


app = Flask(__name__,template_folder='temp')
app.secret_key = "secret key"


# calling config file as per requirement
# if app.config["ENV"] == "production":
#     app.config.from_object("config.ProductionConfig")
# elif app.config["ENV"] == "development":
#     app.config.from_object("config.DevelopmentConfig")
# else:
#     app.config.from_object("config.TestingConfig")


# reading config.json file
conf = open(r"C:\Users\HP\OneDrive - Applied Cloud Computing\flask_practice\flask_app\config.json")
conf_data = conf.read()

# json parsing
conf_data = json.loads(conf_data)


# initializing mysql object
mysql = MySQL()
app.config['MYSQL_HOST'] = conf_data["MYSQL_HOST"]
app.config['MYSQL_USER'] = conf_data["MYSQL_USER"]
app.config['MYSQL_PASSWORD'] = conf_data["MYSQL_PASSWORD"]
app.config['MYSQL_DB'] = conf_data["MYSQL_DB"]
mysql.init_app(app)



@app.route('/')
def home():
    # print(app.config["MYSQL_USER"])
    return render_template("home.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signin_success", methods=['POST'])
def success():
    if request.method=='POST':
        cur = mysql.connection.cursor()
        email = request.form['email']
        password = request.form['password']
        # cur.execute("select email from login where email LIKE %s",[email])
        try:
            cur.execute("INSERT INTO LOGIN VALUES(%s,%s)",(email,password))
            mysql.connection.commit()
            cur.close()
            # result = jsonify(data)
            signin = True
            return render_template("main.html", signin=signin,email=email)
        except:
            signin=False
            return render_template("signin.html",signin=signin)

@app.route('/login_success',methods=['POST'])
def login_success():
    if request.method=='POST':
        cur = mysql.connection.cursor()
        email = request.form['email']
        password = request.form['password']
        cur.execute("SELECT password,email FROM login WHERE email LIKE %s",[email])
        data = cur.fetchall()

        if not data:
            fail = "email_wrong"
            return render_template('login.html', fail=fail)
        else:
            # return str(data[0][0])
            if data[0][0] == password:
                login=True
                return render_template("main.html",login=login,email=email)
            else:
                fail = "password_wrong"
                return render_template("login.html", fail=fail)
                




os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "600548504659-9uapv9g0cfhjsht48nh70oufji0e5q10.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client_secret.json")


# add client secret file into google flow
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)




# create decorator
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401) # authentication required
        else:
            return function()
    return wrapper


@app.route("/google_login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session['state']=state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args['state']:
        abort(500) # state does not match

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token = credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    
    session['google_id'] = id_info.get("sub")
    # if 'google_id' in session:
    #     app.permanent_session_lifetime = timedelta(seconds=5)
        # return redirect("/")
    #     start_time = datetime.datetime.now()
    #     end_time = start_time + datetime.timedelta(0,10)
    #     if start_time > end_time :
    #         print("time matched")
    #         session.pop("google_id",None)
        # print("session_id=",session['google_id'])
        # print("current_time=",start_time)
        # print("end _time =",end_time)
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.pop("google_id",None)
    return redirect("/")

# @app.route("/")
# def index():
#     return "hello world <a href='/google_login'><button>Click here to Google Login</button></a>"

@app.route("/protected_area")
@login_is_required 
def pretected_area():
    
    # app.permanent_session_lifetime = timedelta(seconds=5)
    # session.pop("google_id",None)
    return "Protected <a href='/logout'><button>Logout</button></a>"

 



# facebook authentication using oauth
# Your ngrok url, obtained after running "ngrok http 5000"
URL = "https://679e4c83.ngrok.io"

# FB_CLIENT_ID = os.environ.get("FB_CLIENT_ID")
FB_CLIENT_ID = 259762062401630
FB_CLIENT_SECRET = "6b8a4fc54a76d6005fc742b4ace0ba5e"
# FB_CLIENT_SECRET = os.environ.get("FB_CLIENT_SECRET")

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]


@app.route("/fb-login")
def fb_login():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri=URL + "/fb-callback", scope=FB_SCOPE
    )
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

    print("authorization_url",authorization_url)
    return flask.redirect(authorization_url)
    # return redirect("/protected_area")

@app.route("/fb-callback")
def fb_callback():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/fb-callback"
    )
    print(facebook)
    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response=flask.request.url,
    )

    # Fetch a protected resource, i.e. user profile, via Graph API

    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    email = facebook_user_data["email"]
    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")

    return f"""
    User information: <br>
    Name: {name} <br>
    Email: {email} <br>
    Avatar <img src="{picture_url}"> <br>
    <a href="/">Home</a>
    """
    # return redirect("/protected_area")




if __name__ == "__main__":
    app.run(debug=True)