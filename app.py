import io
from flask import Flask, request, send_file, Response, render_template, jsonify
from flask_sockets import Sockets

from google.protobuf.json_format import MessageToJson
from desmond.thought import DesmondNode
from desmond import types

# This is definitely NOT the right way to do this. What's the right way to
# share protocols? For the actuators, we send a definition of the protocol from
# the receiver to the commander. Another option is to simply have a lightweight
# github repository (or similar) of types that can be pulled in when needed.
# But this is an instance of centralization that would be nice to avoid. But
# then again, how do you know the *name* of the type at all, and do anything
# useful with it. For now, we comprimise here for the sake of the dashboard.
from desmond.contrib import FaceDetection

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


facenode = None
def facenode_instance():
    global facenode
    if facenode is None:
        facenode = DesmondNode("Faces", [FaceDetection], None)
    return facenode

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/data')
def data():
    return jsonify({})

@app.route('/')
def welcome():
    return render_template("index.html")

@sockets.route("/FaceDetection")
def face_detect(ws):
    while not ws.closed:
        data = facenode_instance().recv_or_none(100)
        if data:
            json_string = MessageToJson(data)
            ws.send(json_string)

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
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

