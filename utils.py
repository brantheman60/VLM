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

def delete_table_entry(con, table_id, entry_id):
    cur = con.cursor() # create a cursor to execute SQL commands

    cur.execute(f"DELETE FROM {table_id} WHERE id = {entry_id};")
    con.commit()

def clear_table(con, table_id):
    cur = con.cursor() # create a cursor to execute SQL commands

    cur.execute(f"DELETE FROM {table_id};")
    con.commit()

def get_table_entry(con, table_id, entry_id):
    cur = con.cursor() # create a cursor to execute SQL commands

    res = cur.execute(f"SELECT * FROM {table_id} WHERE id = {entry_id};").fetchall()
    return res