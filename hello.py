from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

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

# Flask_Login stuff
login_manager =LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_colour = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Password stuff!
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string
    def __repr__(self):
        return "<Name %r>" % self.name
    
# Create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

# Create a user form class
class UserForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    username = StringField("Username:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    favourite_colour = StringField("Favourite colour")
    password_hash = PasswordField("Password", validators=[DataRequired(),EqualTo("password_hash2", message="Passwords must be the same")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit") 

# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a PW form class
class PasswordForm(FlaskForm):
    email = StringField("What is your email?", validators=[DataRequired()])
    password_hash = PasswordField("What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Posts form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Slug", validators=[DataRequired()])
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

# Create PW test page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ""
        form.password_hash.data = ""

        # Check user email address
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # Check hashed pw
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html",
        email = email,
        password = password,
        pw_to_check = pw_to_check,
        passed = passed,
        form = form                   
        )

@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username = form.username.data, name=form.name.data, email=form.email.data, favourite_colour=form.favourite_colour.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favourite_colour.data = ""
        form.password_hash = ""
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
    
# Create Json object
@app.route("/date")
def get_current_date():
    return {"Date": date.today()}

# Add an Add Posts page
@app.route("/add-post", methods=["GET", "POST"])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     author=form.author.data,
                     slug=form.slug.data)
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        # Add post data to db
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog post submitted successfully!")

    # Redirect to webpage
    return render_template("add_post.html", form = form)

# Add a View Posts page
@app.route("/posts")
def posts():
    # Grab all posts from db
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

# View a single post
@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# Edit a post
@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        # Add updated entries to db
        db.session.add(post)
        db.session.commit()
        flash("Post updated successfully!")

        return redirect(url_for("post", id=post.id))
    
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)


# Delete a post
@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try: 
        db.session.delete(post_to_delete)
        db.session.commit()

        # Flash message
        flash("Blog post was deleted")

        # Return to posts page
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


    except:
        flash("Whoops! there was a problem deleting this post. Please try again")

        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    
# Create login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create login page
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful!")
                return redirect(url_for("dashboard"))
            
            else:
                flash("Invalid password")

        else:
            flash("User does not exist")

    return render_template("login.html", form=form)

# Create dashboard page
@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")

# Create logout page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have sucessfully logged out")
    return redirect(url_for("login"))



