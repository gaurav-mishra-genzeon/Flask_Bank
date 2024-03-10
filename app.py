from flask import Flask, render_template, url_for,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from dotenv import load_dotenv
import bcrypt
import os

load_dotenv()


app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('DATABASE_URL')
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
db= SQLAlchemy(app)



class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class User(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(100),nullable=True)
    lname=db.Column(db.String(100),nullable=True,unique=True)
    email=db.Column(db.String(100),nullable=True,unique=True)
    password= db.Column(db.String(100),nullable=False)

    def __init__(self,fname,email,lname,password):
        self.fname=fname
        self.email= email
        self.lname=lname
        self.password = self._hash_password(password)
        # self.password= bcrypt.hashpw(password.encode('utf-8'),bcrypt.getsalt()).decode('utf-8')

    
    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8')) 
    

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
       fname=request.form['fname']
       email=request.form['email']
       lname=request.form['lname']
       password=request.form['password']

       new_user= User(fname=fname,email=email,lname=lname,password=password)
       db.session.add(new_user)
       db.session.commit()
    #    flash('Registration successful!', 'success') 
       return redirect('/login')
    
    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():

    if request.method == 'POST':
       email=request.form['email']
       password=request.form['password']
       print(email,password)
       user=User.query.filter_by(email=email).first()
       print(user)

       if user and user.check_password(password):
           print(1)
           session['fname']=user.fname
           session['lname']=user.lname
           session['email']=user.email
           session['password']= user.password
        #    flash('Login successful!', 'success') 
           return redirect('/dashboard')
       else:
           print(2)
           return render_template('login.html',error='Invalid User')
    
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['fname']:
       user=User.query.filter_by(email=session['email']).first()
       return render_template('dashboard.html',user=user)
    
    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

if __name__=="__main__":
    app.run(debug=True)