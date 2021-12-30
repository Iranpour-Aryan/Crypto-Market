import os
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import yfinance as yf


load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=10)

ca = certifi.where()
client = MongoClient(os.environ.get("MONGODB_URI"), tlsCAFile=ca)
app.db = client.crypto_market

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
                app.db.users.insert_one({"username": request.form["username"], "password": hashpass, "email": request.form["email"]})   #Then you add the info into our users collection in our database
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
        return render_template("user.html", username=username)

    else:
        flash("You need to login!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():

    flash("You have logged out!", "info")   #logout and then redirects to login page.

    session.pop("username", None)       #clears the user data once logged out
    return redirect(url_for("login"))

@app.route("/market")
def market():
    BTC_price = yf.download(tickers='BTC-USD', period='10m')
    ETH_price = yf.download(tickers='ETH-USD', period='10m')
    ADA_price = yf.download(tickers='ADA-USD', period='10m')
    XRP_price = yf.download(tickers='XRP-USD', period='10m')
    DOGE_price = yf.download(tickers='DOGE-USD', period='10m')
    SOL_price = yf.download(tickers='SOL-USD', period='10m')
    XLM_price = yf.download(tickers='XLM-USD', period='10m')
    VET_price = yf.download(tickers='VET-USD', period='10m')
    EOS_price = yf.download(tickers='EOS-USD', period='10m')
    THETA_price = yf.download(tickers='THETA-USD', period='10m')
    TRX_price = yf.download(tickers='TRX-USD', period='10m')
    MATIC_price = yf.download(tickers='MATIC-USD', period='10m')
    LTC_price = yf.download(tickers='LTC-USD', period='10m')
    QNT_price = yf.download(tickers='QNT-USD', period='10m')
    LINK_price = yf.download(tickers='LINK-USD', period='10m')
    return render_template('market.html', BTC_price=list(BTC_price['Close'])[0],
                           ETH_price=list(ETH_price['Close'])[0],
                           ADA_price=list(ADA_price["Close"])[0], XRP_price=list(XRP_price["Close"])[0],
                           DOGE_price=list(DOGE_price["Close"])[0],
                           SOL_price=list(SOL_price["Close"])[0], XLM_price=list(XLM_price["Close"])[0],
                           VET_price=list(VET_price["Close"])[0],
                           EOS_price=list(EOS_price["Close"])[0], THETA_price=list(THETA_price["Close"])[0],
                           TRX_price=list(TRX_price["Close"])[0],
                           MATIC_price=list(MATIC_price["Close"])[0], LTC_price=list(LTC_price["Close"])[0],
                           QNT_price=list(QNT_price["Close"])[0],
                           LINK_price=list(LINK_price["Close"])[0]
                           )



if __name__ == "__main__":
    app.secret_key = "hello"
    app.run(debug=True)


