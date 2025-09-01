# Create a Virtual Art Gallery.
# 1: Make template functional (use day 88 as a base)
# 2: Allow user to select an artist to display the artworks.
# 3: Get art data jsons from artsy API in met_art_data.py
# 4: Generate artwork cards. Function to get 10 random artworks from that artist.
# 5: Display 10 random artwork cards.
# Issue: Retrieved json is not correct. Complications with Artsy API, switched to a simpler API.
# NICE TO HAVE: Implement lazy loading in JS once I learn. The website is too slow.

import os
from flask import Flask, redirect, url_for, render_template, request
from flask_bootstrap import Bootstrap5
from forms import ArtMovementForm
from met_art_data import *

# Create the app:
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

# Create MET API client
client = MetAPIClient()

# Get list of artists to display:
with open("artists.txt", 'r') as artists_file:
    txt_data = artists_file.read()
    options_list = txt_data.split("\n")

# Routes of all the pages inside the website:
@app.route("/", methods=['GET', 'POST'])
def home():
    form = ArtMovementForm()
    form.item_id.choices = options_list

    if form.validate_on_submit():
        try:
            selected_option = form.item_id.data
            return redirect(url_for("create_gallery", artist=selected_option))
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return redirect(url_for("home"))

    return render_template("index.html", form=form)

@app.route("/artworks", methods=['GET', 'POST'])
def create_gallery():
    selected_option = request.args.get("artist")  # Extract the artistic movement from the query parameter.
    form = ArtMovementForm()
    form.item_id.choices = options_list

    # Only set the form's selected data if it's a GET request or no form submission is in progress
    if request.method == 'GET':
        form.item_id.data = selected_option  # Set the form's current value to the selected artist from query params

    # Handle form submission (POST request)
    if request.method=='POST' and form.validate_on_submit():
        new_selection = form.item_id.data  # Get new artist selection from form data
        return redirect(url_for("create_gallery", artist=new_selection))  # Redirect with the new selected artist in the query params

    # If an artist is selected, fetch artwork details and render
    if selected_option:
        try:
            artwork_details = client.search_artworks(selected_option)
            return render_template("artworks.html", artist=selected_option, artwork_details=artwork_details, form=form)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return redirect(url_for("home"))
    return render_template("artworks.html", form=form)

if __name__ == "__main__":
    app.run(debug=True, port=5003)