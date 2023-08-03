from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Create flask instance
app = Flask(__name__)
app.config["SECRET_KEY"] = "this is the secret key"

# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

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

# Custom error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create name page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submitted successfully!")

    return render_template("name.html",
        name = name,
        form = form                   
        )


