from flask import Flask, abort, render_template, redirect, url_for, jsonify, render_template, request, flash, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from forms import RegisterForm, LoginForm, TodoListForm, ChallengeForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configue Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI_challenges', "sqlite:///challenges.db")
db.init_app(app)


# CONFIGUE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # challenges* Relate user to a list challenges
    # challenges = relationship("Challenges", back_populates="id")


class Challenges(db.Model):
    __tablename__ = "challenges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # user1 Create reference to the User object. The "posts" refers to the posts property in the User class.
    # user = relationship("User", back_populates="challenges")
    challenge_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # todos* Relate challenge with Todos table
    todos = db.relationship("Todos", backref="challenge", lazy=True)


class Todos(db.Model):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    challenge_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("challenges.id"))
    # challenge1 connect to challenge_id
    # challenge = relationship("Challenges", back_populates="todos")


with app.app_context():
    db.create_all()

# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function()


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user email is already present in the database:
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if user:
            # User already exists
            flash("You've already singed up with that email. Log in instead.")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            username=form.username.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique, so will only return 1 result.
        user = result.scalar()
        if not user:
        # Email doesn't exist
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))  # Redirect, causing a new request cycle
        elif not check_password_hash(user.password, password):
        # Password incorrect
            flash("Password incorrect, please try again")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_user_challenges', username=user.username))
    # Display flash messages after redirect (if any)
    print("Session after redirect:", session)  # This is the session after redirect
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/my_challenges/<username>', methods=["GET", "POST"])
def get_user_challenges(username):
    # Ensure user is logged in.
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Get user challenges
    user = User.query.filter_by(username=username).first()
    user_challenges = Challenges.query.filter_by(user_id=user.id).all()

    # Create new challenge form & functionality
    challenge_form = ChallengeForm()
    if challenge_form.validate_on_submit():
        challenge = challenge_form.challenge_name.data
        new_challenge = Challenges(
            user_id=current_user.id,
            challenge_name=challenge
        )
        db.session.add(new_challenge)
        db.session.commit()
        return redirect(url_for('get_user_challenges', username=username))

    # Add task form & functionality
    task_form = TodoListForm()
    if task_form.validate_on_submit():
        task = task_form.add_task.data
        challenge_id = request.form.get('challenge_id')
        if challenge_id:
            new_task = Todos(
                task=task,
                status=False,
                challenge_id=challenge_id,
            )
            db.session.add(new_task)
            db.session.commit()
            print(challenge_id)
        return redirect(url_for('get_user_challenges', username=username))

    # Update task statuses
    if request.method == "POST":
        challenge_id = request.form.get('challenge_id')
        if challenge_id:
            tasks = Todos.query.filter_by(challenge_id=challenge_id).all()
            for task in tasks:
                task_status = f'task_status_{task.id}'
                if task_status in request.form:
                    task.status = True
                else:
                    task.status = False
            db.session.commit()

    return render_template("challenges.html", task_form=task_form, challenge_form=challenge_form,
                           current_user=current_user, username=username, challenges=user_challenges)


@app.route('/test', methods=["GET", "POST"])
def test_route():
    challenge_form = ChallengeForm()
    if challenge_form.validate_on_submit():
        challenge = challenge_form.challenge_name.data
        print(f"Create challenge: {challenge}")
    task_form = TodoListForm()
    if task_form.validate_on_submit():
        task = task_form.add_task.data
        print(f"Add {task}")
    return render_template('test.html', task_form=task_form, challenge_form=challenge_form,  current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
