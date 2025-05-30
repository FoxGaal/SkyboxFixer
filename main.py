from flask import Flask, request, jsonify, render_template, Response, send_file
import threading
import base64
from PIL import Image
from io import BytesIO
import os
import subprocess
import time
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>', methods=['GET', 'POST'])
def download_link(filename):
    response = send_file(filename)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


subprocess_output = []

@app.route('/events', methods=['GET'])
def client_message():
    uuid = request.args.get('uuid')
    def event_stream():
        while True:
            if subprocess_output and uuid == id:
                output = subprocess_output.pop(0)
                yield output
            time.sleep(0.1)
    return Response(event_stream(), content_type='text/event-stream')


@app.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        data = request.json
        image_data = data['image']
        global id
        id = data['id']

        # Remove the "data:image/png;base64," prefix
        image_data = image_data.split(',')[1]

        image_path = os.path.join('textures', "starfield03.png")

        try :
            command = ['blender', '--version']
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except :
            print('\033[91m'+"Error blender is not in environment variables, are you using microsoft store version? please install from blender.org and run setup"+'\033[0m')
            send_client_message("Error","Failed to start blender, not installed correctly")
            return jsonify({'status': 'failed', 'message': 'Blender error'})
        

        # Start a new thread to process the image in the background
        thread = threading.Thread(target=process, args=(image_data, image_path))
        thread.start()

        return jsonify({'status': 'success', 'message': 'Image is being processed', 'path': image_path})

    except Exception as e:
        # Handle exceptions and send error response
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
def getengines():
    command = ['blender', '--background', '-E', 'help']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout

    # Find the part of the output that lists the engines
    start_phrase = "Blender Engine Listing:"
    if start_phrase in output:
        engines_part = output.split(start_phrase)[1].strip()
        engines = [line.strip() for line in engines_part.splitlines() if line.strip()]
        
        print("Available render engines:")
        for engine in engines:
            print(engine)
        return engines
    else:
        print("Render engines not found")
        return None

def process(image_data, image_path):
    
    send_client_message("Started", "Started rendering the images")
    # Decode the image data
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    
    # Modify render settings to match resolution
    with open("render_settings.json", "r") as jsonFile:
        data = json.load(jsonFile)
        
    size = int(max(image.width/3,image.height/2))
    default = data['default'][0]
    res = default['resolution']
    res["x"] = size
    res["y"] = size

    for engine in getengines():
        if default['engine'] in engine : default['engine'] = engine

    with open("render_settings.json", "w") as jsonFile:
        json.dump(data, jsonFile)
    # Ensure directory exists
    upload_dir = 'textures'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save the image with the provided name
    image.save(image_path)

    process = subprocess.Popen(
        ['blender', 'skyboxFix.blend', '--background', '--python', 'render.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        
        if "Saved:" in line:
            line = line[line.find("Renders\\")+8:]
            line = line[:line.find("\'")]
            send_client_message("Rendered", line)
    
    send_client_message("Finished", "All images done")

def send_client_message(event, message):
    
    subprocess_output.append(f"event: {event}\ndata: {message}\n\n")

if __name__ == '__main__':

    app.run(debug=True)
