from flask import Flask, render_template

# Create flask instance
app = Flask(__name__)

# Create route decorator
@app.route("/")

#def index():
    #return "<h1>Hello World!</h1>"

def index():
    foods = ["pizza","kebab","chicken"]
    return render_template("index.html",
    foods = foods)

@app.route("/user/<name>")

def user(name):
    return render_template("user.html", user_name=name)