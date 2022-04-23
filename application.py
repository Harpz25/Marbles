import os
import re
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from dotenv import load_dotenv
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import websearch, login_required

load_dotenv()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
mail = Mail(app)

db = SQL("sqlite:///marbles.db")


@app.route("/")
@login_required
def index():

    user = db.execute("SELECT* FROM users WHERE id = ?", session["user_id"])
    client_email = (user[0]['email'])
    client_profile = (user[0]['profile'])

    if client_profile == "incomplete":
        message = "complete_profile"
        return render_template("apology.html", message=message)

    keyword = db.execute("SELECT* FROM keywords WHERE id = ?", session["user_id"])
    for item in keyword:
         keyword_1  = item["keyword_1"]
         keyword_2 = item["keyword_2"]

    do_query = "mental health" + ";" + keyword_1 + ";" + keyword_2 + ";ways;take care;improve;"
    dont_query = "mental health" + ";" + keyword_1 + ";" + keyword_2 + ";ways;prevent;causes;"
    event_query = "mental health" + ";" + keyword_1 + ";" + keyword_2 + ";events;online;near me;"

    do_dict = websearch(do_query)
    dont_dict= websearch(dont_query)
    event_dict = websearch(event_query)

    print(do_dict)
    print(dont_dict)
    print(event_dict)


    #getenv() function is used to retrive sensitive information such as personal email address and password that is purposely stored in external environament(.env file)
    sender_email = os.getenv("MAIL_USERNAME")
    newsletter = Message(
                'NEWSLETTER 🗞️',
                sender = ('Marbles', sender_email),
                recipients = [client_email])
    newsletter.html = render_template("newsletter.html", do_dict = do_dict, dont_dict = dont_dict, event_dict = event_dict)
    mail.send(newsletter)

    return render_template("index.html", do_dict = do_dict, dont_dict = dont_dict, event_dict = event_dict)


@app.route("/login", methods= ["GET" ,"POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            message = "username"
            return render_template("apology.html", message=message)

        if not password:
            message = "password"
            return render_template("apology.html", message=message)

        table = db.execute("SELECT name FROM sqlite_master where type = 'table';")
        if (len(table)) <1:
            message = "login_error"
            return render_template("apology.html", message=message)


        user = db.execute("SELECT* FROM users WHERE username = ?", username)


        #user should return only one row with 2 columns(id and hash password)
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            message = "login_error"
            return render_template("apology.html", message=message)
        session["user_id"]  = user[0]["id"]

        return redirect("/")
    else:

        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods = [ "GET", "POST"])
def register():

   if request.method == "POST":

        db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT NOT NULL, hash TEXT NOT NULL, email TEXT NOT NULL,profile TEXT NOT NULL)")

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        hash_password = generate_password_hash(password)

        users = db.execute("SELECT username FROM users")


        used_username = [item['username'] for item in users]

        if not username:
            message = "username"
            return render_template("apology.html", message=message)

        if not email:
            message = "email"
            return render_template("apology.html", message=message)

        if username in used_username:
            message = "used_username"
            return render_template("apology.html", message=message)

        if not password:
            message = "password"
            return render_template("apology.html", message=message)

        if confirmation != password:
            message = "unmatch_password"
            return render_template("apology.html", message=message)

        profile = "incomplete"

        db.execute("INSERT INTO users (username, hash,email,profile) VALUES(?,?,?,?)", username, hash_password, email,profile)

        return redirect("/")

   else:

        return render_template("register.html")


@app.route("/profile", methods = [ "GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        if not request.form.get("physical_health"):
            message = "complete_profile"
            return render_template("apology.html", message=message)

        if not request.form.get("psychological"):
            message = "complete_profile"
            return render_template("apology.html", message=message)

        if not request.form.get("social_relationship"):
            message = "complete_profile"
            return render_template("apology.html", message=message)

        if not request.form.get("environment"):
            message = "complete_profile"
            return render_template("apology.html", message=message)

        if not request.form.get("cope"):
            message = "complete_profile"
            return render_template("apology.html", message=message)

        if not request.form.get("primary_problem"):
            message = "complete_profile"
            return render_template("apology.html", message=message)

        profile_1 =  int(request.form.get("physical_health"))
        profile_2 =  int(request.form.get("psychological"))
        profile_3 = int(request.form.get("social_relationship"))
        profile_4 =  int(request.form.get("environment"))
        profile_5 =  int(request.form.get("cope"))
        primary_problem = request.form.get("primary_problem")

        user = db.execute("SELECT* FROM users WHERE id = ?", session["user_id"])
        user_id = (user[0]['id'])

        new_dict = {"physical_health": [], "psychological": [], "social_relationship": [], "environment": []}

        new_dict.update({"physical_health": profile_1, "psychological": profile_2, "social_relationship": profile_3, "environment": profile_4})
        ini_list = list(new_dict.values())
        min_value = min(ini_list)
        new_list = [x for x in ini_list if min_value == x ]
        if len(new_list) > 1:
          keyword_1 = primary_problem
        else:
           for key,value in new_dict.items():        #items() method is used to iterate through new_dict
               if value == min_value:
                  keyword_1 = key
        if profile_5 < 3:
            keyword_2 = "management"
        else:
             keyword_2 = ("")                      #no supporting keyword will be used if user indicate adequate ability to cope with problems & blankspace will used instead

        profile = "complete"

        db.execute("CREATE TABLE IF NOT EXISTS keywords(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, keyword_1 TEXT NOT NULL, keyword_2 TEXT)")
        db.execute("INSERT INTO keywords(user_id, keyword_1, keyword_2) VALUES(?,?,?)", session['user_id'], keyword_1,keyword_2)
        db.execute("UPDATE users SET profile = ? WHERE id = ?", profile,session['user_id'])

        return redirect("/")

    else:

        return render_template("profile.html")


@app.route("/privacy", methods = ["GET", "POST"])
@login_required
def privacy():

    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not password:
            message = "password"
            return render_template("apology.html", message=message)

        if confirmation != password:
            message = "unmatch_password"
            return render_template("apology.html", message=message)

        hash_password = generate_password_hash(password)

        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash_password,session["user_id"] )

        return redirect("/")

    else:

        users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("privacy.html",users = users)

