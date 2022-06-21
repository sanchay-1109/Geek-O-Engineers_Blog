from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime


local_server=True
with open('templates\config.json','r') as c:
    parameters=json.load(c)["parameters"]


app = Flask(__name__)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['prod_uri']
db=SQLAlchemy(app)

class Contacts(db.Model):
    # sno,name,email,phone_no,message,date
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(20),nullable=False)
    phone_no = db.Column(db.String(12),nullable=False)
    message = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(12),nullable=False)

@app.route("/")
def home():
    return render_template('index.html',parameters=parameters)
       
@app.route("/about")
def about():
    return render_template('about.html',parameters=parameters)

@app.route("/contact", methods=['GET','POST'])
def contact():

    if(request.method=='POST'):
        ''' add entry to database'''
        name=request.form.get('name')
        email=request.form.get('email')
        phone_no=request.form.get('phone_no')
        message=request.form.get('message')

        entry=Contacts(name=name,email=email,phone_no=phone_no,date= datetime.now(),message=message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',parameters=parameters)           

app.run(debug=True)    