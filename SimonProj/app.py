import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Your NASA API Key
API_KEY = "diNv0vCTVUTtrbM9wmSPbvgtgReflUM54F011kvD"

BASE_URL = "https://api.nasa.gov/planetary/apod"

@app.route('/')
def home():
    """
    Renders the main HTML page
    """
    return render_template("index.html")


@app.route('/api/today')
def get_today():
    """
    Returns today's Astronomy Picture of the Day as JSON
    """
    params = {
        "api_key": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    return jsonify(response.json())


@app.route('/search')
def search():
    """
    Example: /search?date=2024-01-01
    Returns APOD for a specific date
    """
    date = request.args.get("date")

    if not date:
        return {"error": "No date provided. Use format YYYY-MM-DD"}, 400

    params = {
        "api_key": API_KEY,
        "date": date
    }

    response = requests.get(BASE_URL, params=params)
    return jsonify(response.json())


if __name__ == "__main__":
    app.run(debug=True)