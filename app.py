from flask import Flask, render_template, url_for,request,redirect,session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
# from flask_wtf.csrf import CSRFProtect
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
# csrf = CSRFProtect(app) 


# class RegistrationForm(FlaskForm):
#     fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
#     lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # submit = SubmitField('Sign Up')


class User(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(100),nullable=True)
    lname=db.Column(db.String(100),nullable=True,unique=True)
    email=db.Column(db.String(100),nullable=True,unique=True)
    password= db.Column(db.String(100),nullable=False)
    balance = db.Column(db.Float, default=0)


    def __init__(self,fname,email,lname,password):
        self.fname=fname
        self.email= email
        self.lname=lname
        self.password = self._hash_password(password)
        self.balance = 0
       
    
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
    if request.method == 'POST':
       fname=request.form['fname']
       email=request.form['email']
       lname=request.form['lname']
       password=request.form['password']

       new_user= User(fname=fname,email=email,lname=lname,password=password)
       db.session.add(new_user)
       db.session.commit()
       flash('Registration successful!') 
       return redirect('/login')
    
    return render_template('register.html')


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()

#     if form.validate_on_submit():
#        fname=request.form['fname']
#        email=request.form['email']
#        lname=request.form['lname']
#        password=request.form['password']

#        new_user= User(fname=fname,email=email,lname=lname,password=password)
#        db.session.add(new_user)
#        db.session.commit()
#        print(new_user)
#        flash('Registration successful!') 
#        return redirect('/login')
    
#     else:
#         for field, errors in form.errors.items():
#             for error in errors:
#                 flash(f'Error in {getattr(form, field).label.text}: {error}', 'error')
        
#     return render_template('register.html',form=[form])


@app.route('/login',methods=['GET','POST'])
def login():

    if request.method == 'POST':
       email=request.form['email']
       password=request.form['password']
    
       user=User.query.filter_by(email=email).first()
     

       if user and user.check_password(password):
           session['user_id'] = user.id
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


@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    user = User.query.get(user_id)

    amount = float(request.form['amount'])

    if amount <= 0:
        flash('Invalid amount for deposit', 'error')
    else:
        user.balance += amount
        db.session.commit()
        flash(f'Amount {amount} deposited successfully', 'success')

    return redirect('/dashboard')



@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    user = User.query.get(user_id)

    amount = float(request.form['amount'])

    if amount <= 0 or amount > user.balance:
        flash('Invalid amount for withdrawal', 'error')
    else:
        user.balance -= amount
        db.session.commit()
        flash(f'Amount {amount} withdrawn successfully', 'success')

    return redirect('/dashboard')


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    user = User.query.get(user_id)

    old_password = request.form['old_password']
    new_password = request.form['new_password']

    if not user.check_password(old_password):
        flash('Incorrect old password', 'error')
    else:
        user.password = user._hash_password(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')

    return redirect('/dashboard')


if __name__=="__main__":
    app.run(debug=True)