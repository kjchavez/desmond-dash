import io
from flask import Flask, request, send_file, Response

from desmond.thought import DesmondNode
from desmond import types

node = None
def get_encoded_image():
    global node
    if node is None:
        node = DesmondNode("MissionControl", [types.Image], None)
    image = node.recv_or_none()
    if image is None or image.encoding != types.Image.JPEG:
        return None

    return image.data

def gen():
    while True:
        frame = get_encoded_image()
        if frame is None:
            print("Error fetching frame. Skipping.")
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame +
               b'\r\n')

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Server is up!"

@app.route('/image')
def hello_world():
    img_data = get_encoded_image()
    if img_data is None:
        print("Error")
        return None

    return send_file(io.BytesIO(img_data),
                         attachment_filename='webcam.jpg',
                         mimetype='image/jpg')

@app.route('/videofeed')
def feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
