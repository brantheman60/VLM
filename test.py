import os
import cv2
import time

from deepface import DeepFace
from gtts import gTTS
import playsound
import speech_recognition as sr
import sounddevice as sd
import wavio

from threading import Thread

cap = cv2.VideoCapture(1)
time.sleep(0.3)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        continue
    cv2.imwrite('face.jpg', frame)



    face_objs = DeepFace.extract_faces(img_path = "face.jpg")
    region = face_objs[0]['facial_area']
    x,y,w,h = region['x'], region['y'], region['w'], region['h']

    # Add annotations
    start = (x,y)
    end = (x+w,y+h)
    cv2.rectangle(frame, start, end, (0, 255, 0), 2)
    
    cv2.imshow('Welcome to Toyota!', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break