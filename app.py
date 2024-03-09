from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from dotenv import load_dotenv
import os

load_dotenv()


app= Flask(__name__)
db= SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']= os.getenv('DATABASE_URL')
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


if __name__=="__main__":
    app.run(debug=True)