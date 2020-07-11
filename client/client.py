import requests
import cv2
import json
import sys
import time


def resize_square(im1, dim):
    h, w = im1.shape[0], im1.shape[1]
    color = [0, 0, 0]
    top, bottom, left, right = 0, 0, 0, 0
    new_im = im1.copy()
    
    if w>h:
        diff = w - h
        if diff%2 == 0:
            top, bottom = diff/2, diff/2
        else:
            top, bottom = diff/2+1, diff/2
        new_im = cv2.copyMakeBorder(new_im, int(top), int(bottom), int(left), int(right), cv2.BORDER_CONSTANT,value=color)

    elif h>w:
        diff = h - w
        if diff%2 == 0:
            left, right = diff/2, diff/2
        else:
            left, right = diff/2+1, diff/2
        new_im = cv2.copyMakeBorder(new_im, int(top), int(bottom), int(left), int(right), cv2.BORDER_CONSTANT,value=color)
        
    new_im = cv2.resize(new_im, (dim,dim), interpolation = cv2.INTER_AREA)
    return new_im


url = 'http://LBdetection-2116243642.us-east-1.elb.amazonaws.com:8080/'

headers = {"Content-Type": "image/png"}

vidcap = cv2.VideoCapture(sys.argv[1])
success, frame = vidcap.read()
frame_nr = 0


while success:
    
    '''
    if frame_nr % 15 != 0:
        success,frame = vidcap.read()
        frame_nr += 1
        continue 
    '''

    frame = resize_square(frame, 600)
    
    images_str = cv2.imencode('.png', frame)[1].tostring()

    tmp_time = time.time()

    response = requests.post(url, headers=headers, data = images_str)
    print(response, " in: ", time.time() - tmp_time)
    
    if response.status_code == 200:
    
        results = json.loads(response.text)

        for key in results:
            
            r = results[key]
            print(r)
            x0, y0, x1, y1, name = r['x0'], r['y0'], r['x1'], r['y1'], r['name']
            if name == '':
                name = "sconosciuto"

            cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 0, 255), 2)
            cv2.rectangle(frame, (x0, y1), (x1, y1+20), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (x0, y1+18), font, 0.7, (255, 255, 255), 1)

        
    cv2.imshow('frame',frame)
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
    
    frame_nr += 1
    success,frame = vidcap.read()

vidcap.release()
cv2.destroyAllWindows()