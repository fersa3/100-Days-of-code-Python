from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import RadioField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import PasswordField, HiddenField
from wtforms.validators import DataRequired, NumberRange


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

# WTForm Add to cart:
class AddToCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    size = RadioField('Size', validators=[DataRequired()])
    color = RadioField('Color', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, message='Please a quantity greater than zero.')], default=1)
