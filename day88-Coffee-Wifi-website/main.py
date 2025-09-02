from re import search
from flask import Flask, render_template, redirect, url_for, jsonify, render_template, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from forms import SearchForm, NewPriceForm, CafeForm
import os
import random

# Create the app:
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(Base):
    __tablename__ = 'cafe'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


# Routes of all the pages inside the website:
@app.route("/", methods=["GET", "POST"])
def home():
    # Ver cómo optimizar el código metiendo el form en una función.
    form = SearchForm()
    result = db.session.execute(db.select(Cafe.location))
    all_cafes_loc = result.scalars().all()

    form.item_id.choices = ["Todos los Cafés",]
    for item in all_cafes_loc:
        if item not in form.item_id.choices:
            form.item_id.choices.append(item)

    if form.validate_on_submit():
        selected_item = form.item_id.data
        if selected_item == "Todos los Cafés":
            return redirect(url_for("all_cafes"))
        else:
            # Redirect to search?loc=location
            return redirect(f"/search?loc={selected_item}")

    return render_template("index.html", form=form)

@app.route("/cafes", methods=["GET", "POST"])
def all_cafes():
    result_all = db.session.execute(db.select(Cafe))
    all_cafes = result_all.scalars().all()

    form = SearchForm()
    result_loc = db.session.execute(db.select(Cafe.location))
    all_cafes_loc = result_loc.scalars().all()

    form.item_id.choices = ["Todos los Cafés", ]
    for item in all_cafes_loc:
        if item not in form.item_id.choices:
            form.item_id.choices.append(item)

    if form.validate_on_submit():
        selected_item = form.item_id.data
        if selected_item == "Todos los Cafés":
            return redirect(url_for("all_cafes"))
        else:
            # Redirect to search?loc=location
            return redirect(f"/search?loc={selected_item}")

    return render_template("all_cafes.html", cafes=all_cafes, form=form)

@app.route("/search", methods=["GET", "POST"])
def get_cafe_at_location():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()

    form = SearchForm()
    result_loc = db.session.execute(db.select(Cafe.location))
    all_cafes_loc = result_loc.scalars().all()

    form.item_id.choices = ["Todos los Cafés", ]
    for item in all_cafes_loc:
        if item not in form.item_id.choices:
            form.item_id.choices.append(item)

    if form.validate_on_submit():
        selected_item = form.item_id.data
        if selected_item == "Todos los Cafés":
            return redirect(url_for("all_cafes"))
        else:
            # Redirect to search?loc=location
            return redirect(f"/search?loc={selected_item}")

    return render_template("all_cafes.html", cafes=all_cafes, form=form)

@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.yes_no_to_boolean(form.has_sockets),
            has_wifi= form.yes_no_to_boolean(form.has_wifi),
            has_toilet=form.yes_no_to_boolean(form.has_toilet),
            can_take_calls= form.yes_no_to_boolean(form.can_take_calls),
            seats=form.seats.data,
            coffee_price=form.coffee_price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("all_cafes"))
    return render_template("add_cafe.html", form=form)

@app.route("/random", methods=["GET"])
def get_random_cafe():
    result =db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return render_template("random.html", cafe=random_cafe)


@app.route("/update-price", methods=["GET", "POST"])
def update_price():
    form = NewPriceForm()
    if request.method == "GET":
        return render_template("update-price.html", form=form)

    if request.method == "POST":
        if request.form.get('_method') == "PATCH":
            if form.validate_on_submit():
                cafe = db.get_or_404(Cafe, form.id.data)
                if cafe:
                    if form.new_price.data:
                        cafe.coffee_price = form.new_price.data
                    db.session.commit()
                    return redirect(url_for("all_cafes"))
                else:
                    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# Deletes a cafe with a particular id.
# To report a cafe closed: /report-closed/17?api-key=TopSecretAPIKey
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403



if __name__ == '__main__':
    app.run(debug=True, port=5001)


