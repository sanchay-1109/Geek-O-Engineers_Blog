from flask import Flask, render_template, request ,session ,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime
import math



local_server=True
with open('templates\config.json','r') as c:
    parameters=json.load(c)["parameters"]


app = Flask(__name__)
app.config.update()
app.secret_key = 'super-secret-key'
{
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 465,
    'MAIL_USE_SSL': True,
    'MAIL_USERNAME': parameters['gmail_user'],
    'MAIL_PASSWORD': parameters['gmail_password']
}
mail=Mail(app)

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
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    # img_file = db.Column(db.String(12), nullable=True)    

@app.route("/")
def home():
    posts=Posts.query.filter_by().all() [0:parameters['no_of_posts']]
    return render_template('index.html',parameters=parameters,posts=posts)
       
@app.route("/about")
def about():
    return render_template('about.html',parameters=parameters)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if "user" in session and session['user']==parameters['admin_user']:
        posts = Posts.query.all()
        return render_template("dashboard.html", parameters=parameters, posts=posts)

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==parameters['admin_user'] and userpass==parameters['admin_password']:
            # set the session variable
            session['user']=username
            posts = Posts.query.all()
            return render_template("dashboard.html", parameters=parameters, posts=posts)
    else:
        return render_template("login.html", parameters=parameters)  

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == parameters['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()

            if sno=='0':
              post = Posts(title=box_title, slug=slug, content=content, tagline=tagline,date=date)
              db.session.add(post)
              db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tagline
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', parameters=parameters, post=post, sno=sno) 

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>" , methods=['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user']==parameters['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


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
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[parameters['gmail_user']],
                          # the recipients is always a list so write in square brackets
                          body="Name : "+name+"\n"+"Email : "+email+"\n"+"Phone Number : "+phone_no+"\n"+"Message : "+message
                          )
    return render_template('contact.html',parameters=parameters)           


@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()

    return render_template('post.html',parameters=parameters,post=post)

app.run(debug=True)  

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(parameters['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(parameters['no_of_posts']):(page-1)*int(parameters['no_of_posts'])+ int(parameters['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('index.html', parameters=parameters, posts=posts, prev=prev, next=next)