from flask import *
import requests
from openai import OpenAI
import io
from PIL import Image
import os
import google.generativeai as gemini
from bot_utilities.api_utils import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image', methods=['POST'])
def image():
    data = request.get_json()

    try:
        prompt = data['prompt']
    except KeyError:
        return "Invalid request, you MUST include a 'prompt' in the json.", 400

    img_url = sdxl(prompt)
    img_response = requests.get(img_url)
    img = Image.open(io.BytesIO(img_response.content))

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/text', methods=['POST'])
def text():
    data = request.get_json()
    try:
        prompt = data['prompt']
    except KeyError:
        return "Invalid request, you MUST include a 'prompt' in the json.", 400
    except Exception as e:
        return "Ouch! An error occured, this is probably our fault. Please report this issue.", 1

    response_data = gen_text(prompt)
    return jsonify(response_data)