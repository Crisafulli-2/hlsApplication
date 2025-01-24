import logging
from flask import Flask, jsonify, request
import requests

# Create a Flask application instance
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for HLS data
hls_data_store = {}

# Define a route for the home page
@app.route('/')
def home():
    # Return a JSON response for the home page
    return jsonify(message="Hello, world. We are building an HLS testing automation suite!")

# Define a route for creating HLS data
@app.route('/hls', methods=['POST'])
def create_hls():
    try:
        # Get JSON data from the request
        data = request.get_json()
        hls_id = len(hls_data_store) + 1
        hls_data_store[hls_id] = data
        # Return a JSON response indicating success and the created HLS data
        return jsonify(message="HLS data created successfully", id=hls_id, data=data), 201
    except Exception as e:
        logger.error(f"Error creating HLS data: {e}")
        return jsonify(message="Error creating HLS data. Please check the data format and try again."), 500

# Define a route for reading HLS data
@app.route('/hls/<int:hls_id>', methods=['GET'])
def read_hls(hls_id):
    try:
        data = hls_data_store.get(hls_id)
        if data:
            return jsonify(data=data)
        else:
            return jsonify(message="HLS data not found"), 404
    except Exception as e:
        logger.error(f"Error reading HLS data with ID {hls_id}: {e}")
        return jsonify(message="Error reading HLS data. Please check the HLS ID and try again."), 500

# Define a route for updating HLS data
@app.route('/hls/<int:hls_id>', methods=['PUT'])
def update_hls(hls_id):
    try:
        data = request.get_json()
        if hls_id in hls_data_store:
            hls_data_store[hls_id] = data
            return jsonify(message="HLS data updated successfully", data=data)
        else:
            return jsonify(message="HLS data not found"), 404
    except Exception as e:
        logger.error(f"Error updating HLS data with ID {hls_id}: {e}")
        return jsonify(message="Error updating HLS data. Please check the data format and HLS ID, then try again."), 500

# Define a route for deleting HLS data
@app.route('/hls/<int:hls_id>', methods=['DELETE'])
def delete_hls(hls_id):
    try:
        if (hls_id) in hls_data_store:
            del hls_data_store[hls_id]
            return jsonify(message="HLS data deleted successfully")
        else:
            return jsonify(message="HLS data not found"), 404
    except Exception as e:
        logger.error(f"Error deleting HLS data with ID {hls_id}: {e}")
        return jsonify(message="Error deleting HLS data. Please check the HLS ID and try again."), 500

# Define a route for fetching and processing an HLS .m3u8 file from a URL
@app.route('/fetch_hls', methods=['POST'])
def fetch_hls():
    url = request.json.get('url')
    if not url:
        return jsonify(message="URL is required"), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        m3u8_content = response.text
        return jsonify(message="HLS .m3u8 file fetched successfully", content=m3u8_content)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch the HLS .m3u8 file from URL {url}: {e}")
        return jsonify(message="Failed to fetch the HLS .m3u8 file. Please check the URL and try again.", error=str(e)), 500

# Run the application if this script is executed directly
if __name__ == '__main__':
    # Enable debug mode for development and run on port 5001
    app.run(debug=True, port=5001)