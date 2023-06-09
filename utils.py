from threading import Thread

# Database Libraries
import pandas as pd
import sqlite3

# TTS and STT Libraries
from gtts import gTTS
import playsound
import speech_recognition as sr
import sounddevice as sd
import wavio
import pyttsx3

OUTPUT_MESSAGE = None

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
    global OUTPUT_MESSAGE
    
    fps = 44100
    while(True):
        recording = sd.rec(duration*fps, samplerate=fps, channels=1)
        OUTPUT_MESSAGE = '<Respond now>'
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
    global OUTPUT_MESSAGE

    # Fix pronounciations for certain words
    pronunciation = message.replace('JAAID', 'Jade')

    ''' gTTS code, which is very limited '''
    tts = gTTS(text=pronunciation, lang='en', slow=False)
    tts.save("message.mp3")
    OUTPUT_MESSAGE = message
    playsound.playsound("message.mp3")
    OUTPUT_MESSAGE = None

    ''' pyttsx3 code, which doesn't work in threads '''
    # tts = pyttsx3.init()
    # tts.setProperty('rate', 175)
    # tts.setProperty('volume', 1.0)
    # tts.setProperty('voice', 'com.apple.voice.compact.en-US.Samantha')
    # tts.say(message)
    # tts.runAndWait()
    # tts.stop()

    ''' pyttsx3 code in speak.py, which still doesn't work in threads '''
    # call(['python3', 'speak.py', message])

''' DATABASES '''
CLIENT_KEYS = {'name': 'TEXT', 'age': 'INTEGER', 'male': 'BOOLEAN',
               'race': 'TEXT', 'emotion': 'TEXT', 'new': 'BOOLEAN',
               'interest': 'TEXT', 'similar': 'TEXT', 'current': 'TEXT'}

def get_client_connection():
    con = sqlite3.connect('clients.db') # create a connection to database
    return con

def view_clients(con):
    cur = con.cursor() # create a cursor to execute SQL commands
    res = cur.execute("SELECT * FROM clients;").fetchall()

    print('clients:')
    for r in res:
        print(r)

def insert_client(con, client):
    cur = con.cursor() # create a cursor to execute SQL commands

    # Create table (if necessary)
    keys_types = [f'{k} {v}' for k, v in zip(CLIENT_KEYS.keys(), CLIENT_KEYS.values())]
    cur.execute("CREATE TABLE IF NOT EXISTS clients({});".format(', '.join(keys_types)))

    # Insert client features into table
    values = [client[key] for key in CLIENT_KEYS.keys()]
    values = [v.replace("'", "''") if type(v) == str else v for v in values] # add escape characters
    cur.execute("INSERT INTO clients VALUES ('{}', {}, {}, '{}', '{}', {}, '{}', '{}', '{}');".format(*values))
    
    con.commit()