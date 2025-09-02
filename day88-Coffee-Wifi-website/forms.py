from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL


# Define class for search form:
class SearchForm(FlaskForm):
    item_id = SelectField('Select Item', validators=[DataRequired()])
    submit = SubmitField('Search')


# Define class for update coffee price form:
class NewPriceForm(FlaskForm):
    id = StringField('Id del Café:', validators=[DataRequired()])
    new_price = StringField('Nuevo precio del café americano:', validators=[DataRequired()])

    submit = SubmitField('Actualizar')


# Define class to create the Form to ADD cafes:
class CafeForm(FlaskForm):
    name = StringField("Nombre de la Cafetería", validators=[DataRequired()])
    map_url = StringField("Ubicación del Café en Google Maps (URL)", validators=[DataRequired(), URL()])
    img_url = StringField("URL de la imagen", validators=[DataRequired(), URL()])
    location = StringField("Zona donde se encuentra el Café", validators=[DataRequired()])
    has_sockets = SelectField("¿Hay sockets para conectar la laptop?", choices=["Sí 😊", "No 😞"],
                               validators=[DataRequired()])
    has_wifi = SelectField("¿Tiene WiFi?", choices=["Sí 😊", "No 😞"],
                              validators=[DataRequired()])
    has_toilet = SelectField("¿Tiene baño?", choices=["Sí 😊", "No 😞"],
                              validators=[DataRequired()])
    can_take_calls = SelectField("¿Se pueden tomar llamadas?", choices=["Sí 😊", "No 😞"], validators=[DataRequired()])
    seats = SelectField("Más o menos, ¿cuántas mesas tiene?", choices=[n for n in range(10, 100, 10)],
                                 validators=[DataRequired()])
    coffee_price = StringField("Precio del café americano:", validators=[DataRequired()])


    submit = SubmitField('Agregar')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def yes_no_to_boolean(self, field):
        if field.data == "Sí 😊":
            has_sockets_bool = 1
        else:
            has_sockets_bool = 0
        return has_sockets_bool

