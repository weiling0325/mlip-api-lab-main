from flask import Flask, request, jsonify, render_template
from analyze import read_image,analyze_image
import logging
from msrest.exceptions import HttpOperationError
app = Flask(__name__, template_folder='templates')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
logger.addHandler(console)

@app.route("/")
def home():
    return render_template('index.html')


# API at /api/v1/analysis/ 
@app.route("/api/v1/analysis/", methods=['GET'])
def analysis():
    # Try to get the URI from the JSON
    try:
        get_json = request.get_json()
        image_uri = get_json['uri']
    except:
        return jsonify({'error': 'Missing URI in JSON'}), 400
    
    # Try to get the text from the image
    try:
        res = read_image(image_uri)
        res1 = analyze_image(image_uri)
        response_data = {
            "read_image_result": res,
            "analyse_image_result": res1
        }
        return jsonify(response_data), 200

        # return jsonify(res1),200
    except HttpOperationError as e:
        print("An error occurred:", e)
        print("Error response:", e.response)
    
        print("Error response:", e.response)
        return jsonify({'error': e.response}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)