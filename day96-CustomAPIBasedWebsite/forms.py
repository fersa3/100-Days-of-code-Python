from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired

# Define class for art movement form:
class ArtMovementForm(FlaskForm):
    item_id = SelectField('Select Item', validators=[DataRequired()])
    submit = SubmitField("Let's start!")
