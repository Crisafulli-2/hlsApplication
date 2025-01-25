import logging
import os
import secrets
import requests
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a Flask application instance
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'m3u8', 'hls'}

# Generate a random secret key
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash(f'File uploaded successfully: {filename}')
                return redirect(url_for('upload_file'))
        elif 'url' in request.form:
            file_url = request.form['url']
            if file_url:
                filename = file_url.split('/')[-1]
                if allowed_file(filename):
                    response = requests.get(file_url)
                    if response.status_code == 200:
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        flash(f'File downloaded and saved successfully: {filename}')
                        return redirect(url_for('upload_file'))
                    else:
                        flash('Failed to download file from URL')
                        return redirect(request.url)
                else:
                    flash('File type not allowed')
                    return redirect(request.url)
            else:
                flash('No URL provided')
                return redirect(request.url)
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)