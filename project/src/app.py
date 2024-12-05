from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from deepface import DeepFace
from tensorflow import keras as tf_keras

# Initialize the Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB max file size
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.secret_key = 'supersecretkey'  # Used for flash messages

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper: Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper: Delete uploaded files to avoid clutter
def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

# Route: Homepage with upload form
@app.route('/')
def index():
    return render_template('upload.html')

# Route: Handle file uploads and perform analysis
@app.route('/upload', methods=['POST'])
def upload_file():
    # Ensure a file was uploaded
    if 'file' not in request.files:
        flash('No file part in the request.')
        return redirect(url_for('index'))

    file = request.files['file']

    # Check for an empty filename
    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('index'))

    # Validate file extension
    if not allowed_file(file.filename):
        flash('Allowed file types are png, jpg, jpeg.')
        return redirect(url_for('index'))

    # Secure the filename to avoid security risks
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Save the uploaded file
        file.save(filepath)
        flash(f'File "{filename}" uploaded successfully.')

        # Analyze the image using DeepFace
        result = DeepFace.analyze(img_path=filepath, actions=['age', 'gender', 'emotion'])

        # Handle result as list or dictionary
        if isinstance(result, list):
            result = result[0]

        # Extract relevant analysis details
        age = result['age']
        gender = result['gender']
        dominant_emotion = result['dominant_emotion']

        # Flash the results to display on the homepage
        flash(f'Estimated Age: {age}')
        flash(f'Gender: {gender}')
        flash(f'Dominant Emotion: {dominant_emotion}')

    except Exception as e:
        flash(f'Error occurred during analysis: {e}')

    finally:
        # Clean up: Delete the uploaded file after analysis
        delete_file(filepath)

    # Redirect back to the homepage to display results
    return redirect(url_for('index'))

# Route: Serve uploaded files (Optional, for debugging)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)