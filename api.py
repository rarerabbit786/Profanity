from flask import Flask, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)

API_KEY= os.environ.get("API_KEY")
API_URL = os.environ.get("API_URL")
# Sapling API settings
# SAPLING_API_KEY = "SICCY2TMCVS8EI95UEQL7NVZVG2JZCGU"
# SAPLING_API_URL = "https://api.sapling.ai/api/v1/profanity"

# Preprocessing function to normalize obfuscated words
def preprocess_text(text: str) -> str:
    """
    Normalize obfuscated text by replacing common obfuscation patterns.
    """
    substitutions = {
        "@": "a",
        "3": "e",
        "!": "i",
        "1": "i",
        "$": "s",
        "0": "o"
    }
    # Replace each obfuscation pattern
    for key, value in substitutions.items():
        text = text.replace(key, value)
    return text

# Profanity Filtering Endpoint
@app.route("/filter_profanity", methods=["POST"])
def filter_profanity():
    """
    Endpoint to filter profanity using Sapling AI.
    """
    # Get JSON input
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Invalid request. 'text' is required."}), 400

    input_text = data["text"]

    # Preprocess the input text to handle obfuscation
    normalized_text = preprocess_text(input_text)

    # Prepare payload for Sapling API
    payload = {
        "key": API_KEY,
        "text": normalized_text
    }

    # Send request to Sapling API
    response = requests.post(API_URL, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Error communicating with the API."}), 500

    sapling_response = response.json()
    print(sapling_response)
    toks = sapling_response.get("toks", [])
    labels = sapling_response.get("labels", [])

    # Identify profane words
    profane_words = [toks[i] for i in range(len(labels)) if labels[i] == 1]

    # Generate censored text
    censored_toks = [
        "*" * len(toks[i]) if labels[i] == 1 else toks[i]
        for i in range(len(toks))
    ]
    censored_text = " ".join(censored_toks)

    # Construct the output
    result = {
        "is_profane": len(profane_words) > 0,
        "profane_words": profane_words,
        "censored_text": censored_text
    }

    return jsonify(result)

# Example Root Endpoint
@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Profanity Filter API"}), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
