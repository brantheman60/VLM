# System libraries
import os
import time
from subprocess import call

import tkinter as tk

# Multi-threading
from threading import Thread

# Computer Vision Libraries
import cv2
from deepface import DeepFace
from PIL import Image, ImageTk

# TTS and STT Libraries
from gtts import gTTS
import playsound
import speech_recognition as sr
import sounddevice as sd
import wavio

# DeepFace.stream('client_database')

# Global Variables
DEFAULT_CAMERA = 1      # 0 for most computers, 1 for Mac M1/M2
DEALERSHIP = 'Audi'     # dealership name
frame = None            # camera frame; not including annotations
client = dict()         # information about the client
features = dict()       # information about the client's desired car
                        # - new: new or used car
                        # - current: what the user is currently driving
                        # - similar: what models the user wants to compare to
                        # - exact: exact model the user wants
finished = False        # whether the client is finished with the pipeline

# Set up engines
cap = cv2.VideoCapture(DEFAULT_CAMERA)

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

# speech-to-text
def STT(duration):
    
    fps = 44100
    while(True):
        recording = sd.rec(duration*fps, samplerate=fps, channels=1)
        sd.wait()
        wavio.write("output.wav", recording, fps, sampwidth=2)

        rec = sr.Recognizer()
        with sr.AudioFile('output.wav') as source:
            audio = rec.record(source)
            try:
                text = rec.recognize_google(audio)
                print('RESPONSE:', text)
                return text
            except:
                TTS('Sorry, I couldn\'t understand you.')

# text-to-speech
def TTS(message):
    ''' gTTS code, which is very limited '''
    tts = gTTS(text=message, lang='en', slow=False)
    tts.save("message.mp3")
    playsound.playsound("message.mp3")

    ''' pyttsx3 code, which doesn't work in threads '''
    # tts = pyttsx3.init()
    # tts.setProperty('rate', 175)
    # tts.setProperty('volume', 1.0)
    # tts.setProperty('voice', 'com.apple.voice.compact.en-US.Samantha')
    # tts.say(message)
    # tts.runAndWait()
    # tts.stop()

    ''' pyttsx3 code in speak.py, which still doens't work in threads '''
    # call(['python3', 'speak.py', message])

# display front camera
def play_video():
    global frame

    time.sleep(0.3)
    while(not finished):
        # Capture frame-by-frame
        ret, screen = cap.read()
        if not ret or screen is None:
            continue
        frame = screen.copy()
        cv2.imwrite('face.jpg', screen)

        # Draw bounding box
        try:
            face_objs = DeepFace.extract_faces(img_path = "face.jpg")
            region = face_objs[0]['facial_area']
            x,y,w,h = region['x'], region['y'], region['w'], region['h']
        
            start = (x,y)
            end = (x+w,y+h)
            cv2.rectangle(screen, start, end, (0, 255, 0), 2)
        except:
            pass
        
        # Add annotations
        for i, val in enumerate(client.values()):
            y0 = y - 40*i
            cv2.putText(screen, str(val), (x+w,y0+h), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Welcome to Toyota!', screen)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    cap.release()

# Do the whole client pipeline
def play_pipeline():
    global finished

    # Simultaneously play greeting and get demographics
    # Note: JAAID is pronounced 'Jade'
    message = f'Welcome to {DEALERSHIP}. I will be your personal shopping assistant today. \
               I have been programmed by the humans at {DEALERSHIP} to streamline your dealership visit. \
               My name is JADE. I am the future of automotive retail. \
               Who do I have the pleasure of meeting today?'
    t1 = Thread(target=TTS, args=(message,))
    t2 = ThreadWithReturnValue(target=get_facial_info)
    t1.start()
    t2.start()
    t1.join()

    # Listen for client's name
    client['name'] = STT(duration=2)

    # Continue the conversation to update desired car features:
    TTS('Hello {}. With a few questions, I will activate the \"Autonomous Showroom\", \
        and assemble an {} IQ team that will provide you with human support.'.format(client['name'], DEALERSHIP))
    TTS('Are you looking for a new or used car today?')
    features['new'] = STT(duration=2)
    TTS('Which model are you interested in seeing today?')
    features['interest'] = STT(duration=3)
    TTS('What vehicle are you comparing the {} to?'.format(features['interest']))
    features['similar'] = STT(duration=3)
    TTS('What vehicle are you replacing?')
    features['current'] = STT(duration=3)

    # Send all info to front desk
    TTS('Thank you. Please wait while I assign you a sales representative to help you.')
    finished = True
    print('\n', '*' * 50, '\n')
    print('Sent to sales representative: ')
    print(client)
    print(features)

def get_facial_info():
    while(not finished):
        # Predict demographics
        try:
            dem = DeepFace.analyze(img_path = 'face.jpg',
                actions = ['age', 'gender', 'race', 'emotion']
            )
        except:
            print('No face detected.')
            continue

        # Save collected facial data to client info
        dem = dem[0]
        client['age']     = dem['age']
        client['gender']  = dem['dominant_gender']
        client['race']    = dem['dominant_race']
        client['emotion'] = dem['dominant_emotion']


t0 = Thread(target=play_pipeline)
t0.start()
play_video()