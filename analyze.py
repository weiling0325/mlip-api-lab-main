from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
import logging
import requests
import json
from msrest.exceptions import HttpOperationError

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials from the config file
with open('config.json', 'r') as file:
    config = json.load(file)

key = config.get('VISION_KEY')
endpoint = config.get('VISION_ENDPOINT')

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10

    # SDK call
    rawHttpResponse = client.read(uri, language="en", raw=True)

    # Get ID from returned headers
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]

    # SDK call
    result = client.get_read_result(operationId)

    # Try API
    retry = 0
    
    while retry < maxRetries:
        if result.status.lower () not in ['notstarted', 'running']:
            break
        time.sleep(1)
        result = client.get_read_result(operationId)
        
        retry += 1
    
    if retry == maxRetries:
        return "max retries reached"

    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
        return res_text
    else:
        return "error"
    
def analyze_image(image_url):
    headers = {
        'Ocp-Apim-Subscription-Key': key,
    }
     
    # SDK call
    try:
        # Call recognize_printed_text API
        result = client.recognize_printed_text(url = image_url, custom_header=headers, language="en", raw=False)
    except HttpOperationError as e:
        print("An error occurred:", e)
        print("Error response:", e.response)

    ocr_result = {
            "language": result.language,
            "orientation": result.orientation,
            "textAngle": result.text_angle,
            "regions": []
        }

    for region in result.regions:
        region_data = {
            "boundingBox": region.bounding_box,
            "lines": []
        }
        for line in region.lines:
            line_data = {
                "boundingBox": line.bounding_box,
                "words": [{"boundingBox": word.bounding_box, "text": word.text} for word in line.words]
            }
            region_data["lines"].append(line_data)
        ocr_result["regions"].append(region_data)

    # Return the JSON response
    return ocr_result
