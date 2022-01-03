import os
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=10)

ca = certifi.where()
client = MongoClient(os.environ.get("MONGODB_URI"), tlsCAFile=ca)
app.db = client.crypto_market

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'16',
  'convert':'USD'
}
headers = {
    "X-CMC_PRO_API_KEY": '498cd818-76c9-477e-8327-8c6768bbacf8',
    "Accepts" : 'application/json'
}




@app.route('/')
def home():
    return render_template("index.html")    #home page.

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if(request.form["username"] == "" or request.form["email"] == "" or request.form["password"] == ""):
            return render_template("register.html", error="You must fill in all three required information")
        else:
            existing_user = app.db.users.find_one({'username': request.form["username"]})
            # we check if there's a username in our database with the same username as the one being submitted in the form.

            if existing_user is None:   #If there doesn't exists that username
                hashpass = generate_password_hash(request.form["password"]) #Then you generate a hashed password for security for database
                app.db.users.insert_one({"username": request.form["username"], "password": hashpass, "email": request.form["email"], "wallet": 10000, "coins": []})   #Then you add the info into our users collection in our database
                return redirect(url_for("user")) #You get redirected to user page, then redirected to login.

            else:   #If there exists a user in database with that username in form,
                return render_template("register.html", error="Username already exists")


    return render_template("register.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":   # If the request method is POST
        user = app.db.users.find_one({'username': request.form['username']})   # we try and find a user with that same username in our database
        if user is not None:    #We then check if there exists a user with the form username
            if check_password_hash(user['password'], request.form['password']): #If there is a user, we check if the passwords are the same
                session.permanent = True    #Once passwords are the same, we create a session for user and let them know they have logged in
                session['username'] = request.form['username']
                flash("You have logged in!")
                return redirect(url_for("user"))    #Direct them to the user page
            else:   #If password isn't the same as the one stored in database, you retry.
                return render_template("login.html", msg= flash("Invalid username or Password. Please Try Again"))
        return render_template("login.html", msg=flash("Invalid Username"))    # return this statement when there is no corresponding username
    else:
        if "username" in session:                #if user is logged in
            flash("You are already logged in!")
            return redirect(url_for("user"))    #then you go to user page
        return render_template("login.html")    #If username isn't in the session after registrating, we want it to log in


@app.route("/user")
def user():
    if "username" in session:   #You cannot access the user page until you are successfully logged in
        username = session["username"]
        user_1 = app.db.users.find_one({"username": f"{username}"})

        wallet = user_1["wallet"]

        return render_template("user.html", username=username, wallet = wallet)

    else:
        flash("You need to login!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():

    flash("You have logged out!", "info")   #logout and then redirects to login page.

    session.pop("username", None)       #clears the user data once logged out
    return redirect(url_for("login"))

@app.route("/market",methods=["POST", "GET"])
def market():
    data_price = []
    data_symbols = []
    session_market = Session()
    session_market.headers.update(headers)
    try:
        response = session_market.get(url, params=parameters)
        data = json.loads(response.text)['data']
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    for dt in data:
        data_price.append(dt['quote']['USD']['price'])

    for dt in data:
        data_symbols.append(dt['symbol'])

    if request.method == "POST":
        try:
            response = session_market.get(url, params=parameters)
            data = json.loads(response.text)['data']
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

        username = session["username"]
        user_1 = app.db.users.find_one({"username": f"{username}"})
        wallet = user_1["wallet"]

        num_coins = request.form["num_coins"]
        coin = request.form["myCoins"]

        new_dt = {}

        for dt in data:
            if coin == dt['symbol']:
                new_dt = dt


        if (type(num_coins) != int) or int(num_coins) <= 0:
            flash("Please enter an appropriate integer value!")
            return redirect(url_for("market"))
        elif new_dt == {}:
            flash("Please choose one of the above coins, except for SHIB.")
            return redirect(url_for("market"))
        else:
            coin_price = new_dt['quote']['USD']['price']
            if coin_price * int(num_coins) > wallet:
                flash("Sorry but you do not have enough in your wallet make this purchase")
                return redirect(url_for("market"))
            else:
                flash("You have purchased the following item!")
                return redirect(url_for("user"))

    else:

        if "username" in session:
            username = session["username"]
            user_1 = app.db.users.find_one({"username": f"{username}"})

            wallet = user_1["wallet"]

            try:
                return render_template('market.html',data_price=data_price,wallet=wallet)
            except KeyError:
                flash("Sorry the market is API is a bit slow!")
                return redirect(url_for("user"))

        flash("You need to login to access the market")
        return redirect(url_for("login"))





if __name__ == "__main__":
    app.secret_key = "hello"
    app.run(debug=True)


