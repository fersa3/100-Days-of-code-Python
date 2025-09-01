from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm to register new users:
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField('Sign up')


# WTForm to login existing users:
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


# WTForm to create a new challenge:
class ChallengeForm(FlaskForm):
    challenge_name = StringField("New challenge name", validators=[DataRequired()])
    submit = SubmitField("Create new Challenge")


# WTForm to create a new task:
class TodoListForm(FlaskForm):
    add_task = StringField("Add task", validators=[DataRequired()])
    submit = SubmitField("Add")

