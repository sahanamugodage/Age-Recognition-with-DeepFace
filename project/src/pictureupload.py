# This is the Simple Picture Uploading File in Falsk 
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

# Initialize the Flask app
app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size
app.secret_key = 'supersecretkey'  # For flash messages

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is provided
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    # If no file is selected
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # If the file is allowed, save it
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded')
        return redirect(url_for('index'))

    flash('Allowed file types are png, jpg, jpeg, gif')
    return redirect(request.url)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create the folder if it doesn't exist
    app.run(debug=True)
