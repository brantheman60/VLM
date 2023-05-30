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

# DeepFace.stream('client_database')

# Global Variables
DEFAULT_CAMERA = 1      # 0 for most computers, 1 for Mac M1/M2
frame = None            # camera frame; not including annotations
client = dict()         # information about the client
features = dict()       # information about the client's desired car
                        # - new: new or used car
                        # - current: what the user is currently driving
                        # - similar: what models the user wants to compare to
                        # - exact: exact model the user wants
finished = False        # whether the client is finished with the pipeline

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
def SST(duration):
    
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
    tts = gTTS(text=message, lang='en', slow=False)
    tts.save("message.mp3")
    playsound.playsound("message.mp3")

# display front camera
def play_video():
    global frame

    cap = cv2.VideoCapture(DEFAULT_CAMERA)
    time.sleep(0.3)
    while(True):
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

# Do the whole client pipeline
def play_pipeline():

    # Simultaneously play greeting and get demographics
    t1 = Thread(target=TTS, args=('Hello, welcome to the Toyota car dealership. \
                                Before we begin, please tell me what name you go by.',))
    t2 = ThreadWithReturnValue(target=get_facial_info)
    t1.start()
    t2.start()
    t1.join()
    # t1.join()
    # dem = t2.join()

    # Listen for client's name
    client['name'] = SST(duration=3)

    # Continue the conversation to update desired car features:
    TTS('Hi {}. To start off, are you looking for a specific car or just browsing?'.format(client['name']))
    response = SST(duration=3)
    if 'browsing' in response:
        TTS('Great! Are you looking for a new car or a used car?')
        features['new'] = SST(duration=3)
        TTS('Alright. What car are you currently driving?')
        features['current'] = SST(duration=3)
        TTS('And finally, what car models are you looking for or comparing to?')
        features['similar'] = SST(duration=5)
    else:
        TTS('Great! What car or cars are you looking for?')
        features['exact'] = SST(duration=5)

    # Send all info to front desk
    TTS('Thank you. Please wait while I assign you a sales reprsentative to help you.')
    print('\n', '*' * 50, '\n')
    print('Sent to sales representative: ')
    print(client)
    print(features)

def get_facial_info():
    while(True):
        # Predict demographics
        try:
            dem = DeepFace.analyze(img_path = 'face.jpg',
                actions = ['age', 'gender', 'race', 'emotion']
            )
        except ValueError as ve:
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




# def get_facial_info_image(img_path):

#     # Predict demographics
#     try:
#         dem = DeepFace.analyze(img_path = img_path,
#             actions = ['age', 'gender', 'race', 'emotion']
#         )
#         dem = dem[0]
#     except ValueError as ve:
#         print('No face detected.')
#         exit()

#     # Print demographics
#     print('Age:', dem['age'])
#     print('Gender:', dem['dominant_gender'])
#     print('Race:', dem['dominant_race'])
#     print('Emotion:', dem['dominant_emotion'])

#     # Get region of face
#     region = dem['region']
#     dem['start'] = (region['x'], region['y'])
#     dem['end'] = (region['x'] + region['w'], region['y'] + region['h'])

#     return dem