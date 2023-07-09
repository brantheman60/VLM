from threading import Thread

# Database Libraries
import numpy as np
import pandas as pd
import sqlite3

# TTS and STT Libraries
from gtts import gTTS
import playsound
import speech_recognition as sr
import sounddevice as sd
import wavio
import pyttsx3

# Other Libraries
import webbrowser
import cv2
from urllib.request import Request, urlopen

# Sample customers and sales reps
CLIENT1 = {'name': 'Adam',
           'age': 60,
           'male': True,
           'race': 'white',
           'emotion': 'angry',
           'new': True,
           'interest': "I don't know",
           'compare': "Range Rover",
           'current': '2016 Ford Focus'}

CLIENT2 = {'name': 'Brenda',
           'age': 16,
           'male': False,
           'race': 'latino',
           'emotion': 'happy',
           'new': True,
           'interest': 'Audi A6',
           'compare': "Audi Q3",
           'current': 'Honda Civic'}

CLIENT3 = {'name': 'Cameron',
           'age': 25,
           'male': True,
           'race': 'black',
           'emotion': 'sad',
           'new': False,
           'interest': 'Audi A1',
           'compare': "Audi A4",
           'current': "I don't drive"}

SALES1  = {'name': 'Xavier',
           'age': 35,
           'male': True,
           'race': 'latino',
           'quality': 9.5}

SALES2  = {'name': 'Yolanda',
           'age': 41,
           'male': False,
           'race': 'white',
           'quality': 7.2}

SALES3  = {'name': 'Zachary',
           'age': 27,
           'male': True,
           'race': 'black',
           'quality': 6.6}

OUTPUT_MESSAGE = None
rec = sr.Recognizer()
with sr.Microphone() as source:
    rec.adjust_for_ambient_noise(source)

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
def STT():
    global OUTPUT_MESSAGE
    
    while(True):
        with sr.Microphone() as source:
            OUTPUT_MESSAGE = '<Respond now>'
            audio = rec.listen(source)

            try:
                text = rec.recognize_google(audio)
                print('RESPONSE:', text)
                return text
            except:
                TTS('Sorry, I couldn\'t understand you.')

    # fps = 44100
    # while(True):
    #     recording = sd.rec(duration*fps, samplerate=fps, channels=1)
    #     OUTPUT_MESSAGE = '<Respond now>'
    #     sd.wait()
    #     wavio.write("output.wav", recording, fps, sampwidth=2)

    #     rec = sr.Recognizer()
    #     with sr.AudioFile('output.wav') as source:
    #         audio = rec.record(source)
    #         try:
    #             text = rec.recognize_google(audio)
    #             print('RESPONSE:', text)
    #             return text
    #         except:
    #             TTS('Sorry, I couldn\'t understand you.')

# text-to-speech
def TTS(message):
    global OUTPUT_MESSAGE

    # Fix pronounciations for certain words
    pronunciation = message.replace('JAAID', 'Jade')

    ''' gTTS code, which is very limited '''
    tts = gTTS(text=pronunciation, lang='en', slow=False)
    tts.save("message.wav")
    OUTPUT_MESSAGE = message
    playsound.playsound("message.wav")
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
               'interest': 'TEXT', 'compare': 'TEXT', 'current': 'TEXT'}
SALES_KEYS  = {'name': 'TEXT', 'age': 'INTEGER', 'male': 'BOOLEAN',
               'race': 'TEXT', 'quality': 'REAL'}

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
def get_database_connection():
    con = sqlite3.connect('database.db') # create a connection to database
    con.row_factory = dict_factory # SELECT returns a dictionary instead of a tuple
    return con

def get_table(con, table_name):
    cur = con.cursor() # create a cursor to execute SQL commands
    res = cur.execute(f"SELECT * FROM {table_name};").fetchall()
    return res

def view_table(con, table_name):
    res = get_table(con, table_name)

    print(f'{table_name}:')
    for r in res:
        print(r)
    print('\n')

def insert_table_entry(con, table_name, row):
    cur = con.cursor() # create a cursor to execute SQL commands
    
    if table_name == 'clients':
        KEYS = CLIENT_KEYS
    elif table_name == 'sales':
        KEYS = SALES_KEYS
    else:
        raise Exception('Invalid table name')

    # Create table (if necessary)
    keys_types = [f'{k} {v}' for k, v in zip(KEYS.keys(), KEYS.values())]
    cur.execute("CREATE TABLE IF NOT EXISTS {}(id INTEGER PRIMARY KEY AUTOINCREMENT, {});"
                .format(table_name, ', '.join(keys_types)))

    # Insert row features into table
    columns_str = ', '.join(KEYS.keys())

    values = [row[k] for k in KEYS.keys()]
    values = [v.replace("'", "''") if type(v) == str else v for v in values] # add escape characters
    values_str = [f"'{v}'" if k=='TEXT' else str(v) for k, v in zip(KEYS.values(), values)]
    values_str = ', '.join(values_str)
    cur.execute("INSERT INTO {} ({}) VALUES ({});".format(table_name, columns_str, values_str))
    con.commit() # commit changes to database

    # Finally, return the id of the inserted row
    id = cur.execute("SELECT id FROM {} ORDER BY id DESC LIMIT 1;".format(table_name)).fetchone()['id']
    return id

def delete_table_entry(con, table_id, entry_id):
    cur = con.cursor() # create a cursor to execute SQL commands
    cur.execute(f"DELETE FROM {table_id} WHERE id = {entry_id};")
    con.commit()

def drop_table(con, table_id):
    cur = con.cursor() # create a cursor to execute SQL commands
    cur.execute(f"DROP TABLE {table_id};")
    con.commit()

def clear_table(con, table_id):
    cur = con.cursor() # create a cursor to execute SQL commands
    cur.execute(f"DELETE FROM {table_id};")
    con.commit()

def get_table_entry(con, table_id, entry_id):
    cur = con.cursor() # create a cursor to execute SQL commands
    res = cur.execute(f"SELECT * FROM {table_id} WHERE id = {entry_id};").fetchone()
    return res



''' Web-related Tasks '''
def open_url(url):
    print('Opening URL:', url)
    print(webbrowser.open(url))



''' CV Tasks '''
def rescale(image, ratio):
    width = int(image.shape[1] * ratio)
    height = int(image.shape[0] * ratio)
    return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

def resize(image, width=None, height=None):
    if width is None and height is None:
        return image
    
    if width is None:
        ratio = height / image.shape[0]
        width = image.shape[1] * ratio
    elif height is None:
        ratio = width / image.shape[1]
        height = image.shape[0] * ratio
    
    return cv2.resize(image, (int(width), int(height)), interpolation = cv2.INTER_AREA)

def pic_in_pic(big, small, x=0, y=0, center=True):
    x, y = int(x), int(y)
    big_cpy = big.copy()
    small_x, small_y, _ = small.shape
    if center:
        x -= small_x//2
        y -= small_y//2
    
    big_cpy[x:x+small_x, y:y+small_y] = small
    return big_cpy

def pics_in_pic(big, small_arr, x_arr, y_arr, center=True):
    big_cpy = big.copy()
    for small, x, y in zip(small_arr, x_arr, y_arr):
        big_cpy = pic_in_pic(big_cpy, small, x, y, center)
    return big_cpy

def image_from_url(url):
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    image = urlopen(req).read()
    arr = np.asarray(bytearray(image), dtype=np.uint8)
    return cv2.imdecode(arr, -1)