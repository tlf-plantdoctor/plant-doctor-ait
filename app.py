import os
from flask import Flask, request, jsonify
import replicate
from googletrans import Translator
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Replicate
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

translator = Translator()

@app.route("/")
def home():
    return "Plant Doctor AI is live!"

@app.route("/diagnose", methods=["POST"])
def diagnose():
    data = request.json
    image_url = data.get("image_url")
    lang = data.get("lang", "en")

    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    try:
        output = replicate_client.run(
            "nohamoamary/nabtah-plant-disease:cc7351fcbe261aa91e6a00bbfba48e60bdf7a4fd24b5aeeb5d664d469d59145b",
            input={"image": image_url}
        )

        disease = output["prediction"]
        description = output["description"]
        treatment = output["treatment"]

        # Translate if language is Arabic
        if lang == "ar":
            disease = translator.translate(disease, dest="ar").text
            description = translator.translate(description, dest="ar").text
            treatment = translator.translate(treatment, dest="ar").text

        return jsonify({
            "disease": disease,
            "description": description,
            "treatment": treatment
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
