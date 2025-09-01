from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import binascii
import os

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap5(app)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_colour_palette(filename):
    num_colours= 10
    # Read image
    with Image.open(os.path.join('static\images', filename)) as im:
        im = im.resize((150, 150))
        ar = np.asarray(im)
        shape = ar.shape
        ar = ar.reshape(np.prod(shape[:2]), shape[2]).astype(float)
    # Find clusters with SciPy:
    codes, dist = scipy.cluster.vq.kmeans(ar, num_colours)
    #Assign codes to pixels:
    vecs, dist = scipy.cluster.vq.vq(ar, codes)
    # Count occurrences of each code (cluster):
    counts, bins = np.histogram(vecs, len(codes))
    total_pixels = np.sum(counts)
    # Sort codes by frequency:
    sorted_indices = np.argsort(counts)[::-1] # sort in descending order
    # Get the 10 most frequent colors:
    top_10_colours = []
    for _ in sorted_indices:
        peak = codes[_]
        colour_hex = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        percentage = round((counts[_]/total_pixels)*100,2)
        top_10_colours.append((colour_hex, percentage))
    return top_10_colours # Return list of top colors and their counts


@app.route('/', methods=["GET", "POST"])
def home():
    ex_file = "images/AppBreweryWallpaper 5.jpg"
    ex_top_10_colours = get_image_colour_palette(filename="AppBreweryWallpaper 5.jpg")
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No selected file.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            top_10_colours = get_image_colour_palette(filename=filename)
            return render_template('index.html', img_file=f'images/{filename}', colours=top_10_colours)
        else:
            flash('(Only .png, .jpg, .jpeg formats allowed).')
            return redirect(request.url)
    return render_template('index.html', img_file=ex_file, colours=ex_top_10_colours)

if __name__ == "__main__":
    app.run(debug=True)
