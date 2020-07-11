import cv2
import sys
import numpy as np
import os
import requests
import json
from PIL import Image
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.append("../RetinaFace/")
from retinaface import RetinaFace

class face_detection_component:

  def __init__(self, model_path, url):
    self.thresh = 0.8
    self.detector = RetinaFace(model_path, 0, -1, 'net3')
    self.url_face_recognition = url
    self.headers = {"Content-Type": "image/png"}


  def detection(self,img):

    final_results = {}

    count = 1

    scales = [img.shape[0], img.shape[1]]
  
    im_shape = img.shape
    target_size = scales[0]
    max_size = scales[1]
    im_size_min = np.min(im_shape[0:2])
    im_size_max = np.max(im_shape[0:2])
  
    im_scale = float(target_size) / float(im_size_min)
  
    if np.round(im_scale * im_size_max) > max_size:
      im_scale = float(max_size) / float(im_size_max)

    scales = [im_scale]

    for c in range(count):
      faces, landmarks = self.detector.detect(img, self.thresh, scales=scales, do_flip=False)
    
    if faces is not None:
      
      for i in range(faces.shape[0]):
        box = faces[i].astype(np.int)

        color = (0,0,255)
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)

        x0, y0, x1, y1, _ = box
        x0 = int(x0 - 0.2*(x1 - x0)) if x0 - 0.2*(x1 - x0) >= 0 else x0
        y0 = int(y0 - 0.2*(y1 - y0)) if y0 - 0.2*(y1 - y0) >= 0 else y0
        x1 = int(x1 + 0.2*(x1 - x0)) if x1 + 0.2*(x1 - x0) <= im_shape[1] else x1
        y1 = int(y1 + 0.2*(y1 - y0)) if y1 + 0.2*(y1 - y0) <= im_shape[0] else y1

        face_image = img[y0:y1, x0:x1]
	      name = "sconosciuto"

        images_str = cv2.imencode('.png', face_image)[1].tostring()
	      response = requests.post(self.url_face_recognition, headers=self.headers, data = images_str)
	      if response.status_code == 200:

          results = json.loads(response.text)    
          name = results['name']

        x0, y0, x1, y1, _ = box
        final_results[i] = {
                      "x0": x0,
                      "y0": y0,
                      "x1": x1,
                      "y1": y1,
                      "name": name
              }

    return json.dumps(final_results)



face_detection_obj = face_detection_component('./models/retinaface-R50/R50',"http://Loadbalancerrecognition-830924392.us-east-1.elb.amazonaws.com:8080/")



class face_detection_server_h(BaseHTTPRequestHandler):
    
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
        
        
        global face_detection_obj
        frame_results = face_detection_obj.detection(open_cv_image)
                
        self._set_response()
        self.wfile.write(frame_results.encode())

        
server_class=HTTPServer
handler_class = face_detection_server_h
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