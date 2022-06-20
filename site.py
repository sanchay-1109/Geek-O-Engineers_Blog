from flask import Flask, render_template

app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return render_template('index.html')
       
# @app.route("/about")
# def about():
#     name="sanchay"
#     return render_template('about.html',name=name)

@app.route("/site")
def site():
    
    return render_template('bootstrap.html')           

app.run(debug=True)    