*************************************************************************
Per l'esecuzione del sistema è possibile scaricare ai seguenti link: 
https://hub.docker.com/repository/docker/camillo4eyes/web-app-recognition
https://hub.docker.com/repository/docker/camillo4eyes/face-detection
le immagini dei container preconfigurati.

Server detection: eseguendo il comando "python face_detection_server_2.py" presente nel path /usr/insigthface/server_detection
Server recognition: eseguendo il comando "python3 server.py" presente nel path /usr/server_recognition

Per eseguire il client: "python client.py /path_video"

Inoltre è necessario modificare gli URL presenti negli script "client.py" e "face_detection_server_2.py" nella seguente maniera:
-Nel file client.py inserire l'URL del server di detection (o eventuale LB).
-Nel file face_detection_server_2.py inserire l'URL del server di recognition (o eventuale LB).
*************************************************************************