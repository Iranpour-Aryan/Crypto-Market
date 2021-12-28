import os

from werkzeug.security import generate_password_hash, check_password_hash
import certifi
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=10)

ca = certifi.where()
client = MongoClient(os.environ.get("MONGODB_URI"), tlsCAFile=ca)
app.db = client.crypto_market

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        existing_user = app.db.users.find_one({'username': request.form["username"]})

        if existing_user is None:
            hashpass = generate_password_hash(request.form["password"])
            app.db.users.insert_one({"username": request.form["username"], "password": hashpass})
            return redirect(url_for("user"))

        else:
            return render_template("register.html", error="Username already exists")


    return render_template("register.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        print(request.form['username'])
        user = app.db.users.find_one({'username': request.form['username']})
        if user is not None:
            if check_password_hash(user['password'], request.form['password']):
                session.permanent = True
                session['username'] = request.form['username']
                flash("You have logged in!")
                print("bob")
                return redirect(url_for("user"))
            else:
                print("nine")
                return render_template("login.html", msg="Invalid username or Password. Please Try Again")
        return "Invalid Username"    # return the user page after logging in
    else:
        print("jim")
        if "username" in session:                #if user is logged in
            flash("You are already logged in!")
            return redirect(url_for("user"))    #then you go to user page
        return render_template("login.html")


@app.route("/user")
def user():
    if "username" in session:
        username = session["username"]
        return render_template("user.html", username=username)

    else:
        flash("You need to login!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():

    flash("You have logged out!", "info")

    session.pop("username", None)       #clears the user data once logged out
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.secret_key = "hello"
    app.run(debug=True)


