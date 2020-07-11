import face_recognition
from http.server import BaseHTTPRequestHandler, HTTPServer
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import os
import json

class face_recognition_component:
    
    def __init__(self, dataset_face_location):
        self.known_face_encodings = []
        self.known_face_names = []
        
        for file in os.listdir(dataset_face_location):
            if file.endswith(".jpg"):
                face_name = file.split(".jpg")[0]
                path_face = os.path.join(dataset_face_location, file)
                face_image = face_recognition.load_image_file(path_face)
                face_encoding = face_recognition.face_encodings(face_image)[0]
                
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(face_name)

                
    def detection(self, frame):
        
        results = {
            "x0": -1,
            "y0": -1,
            "x1": -1,
            "y1": -1,
            "name": ""
        } 
        
        face_locations = []
        face_encodings = []
        face_names = []


        small_frame = frame
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:

            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "sconosciuto"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            results = {
                "x0": left,
                "y0": top,
                "x1": right,
                "y1": bottom,
                "name": name
            } 
            return json.dumps(results)
        
        return json.dumps(results)

face_recognition_obj = face_recognition_component("./face/")

class face_recognition_server_h(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        #self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET {}".format(self.path).encode('utf-8'))

    def do_POST(self):
            
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length) 
        
        images_decoded = Image.open(BytesIO(post_data))
        open_cv_image = np.array(images_decoded) 
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        
        
        global face_recognition_obj
        frame_results = face_recognition_obj.detection(open_cv_image)
                
        self._set_response()
        self.wfile.write(frame_results.encode())

        
server_class=HTTPServer
handler_class = face_recognition_server_h
port=8080

server_address = ('', port)
httpd = server_class(server_address, handler_class)
print('Starting...\n')

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print('Stopping...\n')
