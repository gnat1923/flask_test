from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create flask instance
app = Flask(__name__)
# Add database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Secret key
app.config["SECRET_KEY"] = "this is the secret key"
# Initialise the database
db = SQLAlchemy(app)
app.app_context().push()

# Create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a string
    def __repr__(self):
        return "<Name %r>" % self.name
    
# Create a user form class
class UserForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    submit = SubmitField("Submit")

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

@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        flash("User added successfully")

    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
                            form=form,
                            name=name,
                            our_users=our_users)


