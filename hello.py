from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Create flask instance
app = Flask(__name__)
# Add database
# Old SQLite db
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# New MySQL db
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:1234@localhost/our_users'

# Secret key
app.config["SECRET_KEY"] = "this is the secret key"
# Initialise the database
db = SQLAlchemy(app)
app.app_context().push()

migrate = Migrate(app, db)

# Create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_colour = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a string
    def __repr__(self):
        return "<Name %r>" % self.name
    
# Create a user form class
class UserForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    favourite_colour = StringField("Favourite colour")
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
            user = Users(name=form.name.data, email=form.email.data, favourite_colour=form.favourite_colour.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        form.favourite_colour.data = ""
        flash("User added successfully")

    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
                            form=form,
                            name=name,
                            our_users=our_users)

# Update database record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favourite_colour = request.form["favourite_colour"]
        try:
            db.session.commit()
            flash("User updated sucessfully!")
            return render_template("update.html",
                                   form = form,
                                   name_to_update = name_to_update)
        
        except:
            db.session.commit()
            flash("Error! Looks like there was a problem... please try again")
            return render_template("update.html",
                                   form = form,
                                   name_to_update = name_to_update)
        
    else:
        return render_template("update.html",
                                   form = form,
                                   name_to_update = name_to_update,
                                   id=id)
    
# Delete a record
@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")
        our_users = Users.query.order_by(Users.date_added)

        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)
    
    except:
        flash("Whoops, there was an error deleting this user")
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)



