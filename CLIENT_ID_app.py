# System libraries
import os
import time
import sys
from subprocess import call
from utils import *
import utils

# App libraries
import tkinter as tk
from tkinter import messagebox
from tkinter import font

# Multi-threading
from threading import Thread

# Computer Vision Libraries
import cv2
from deepface import DeepFace
from PIL import Image, ImageTk

# DeepFace.stream('client_database')

# Global Variables
DEFAULT_CAMERA = 1      # 0 for most computers, 1 for Mac M1/M2
DEALERSHIP = 'Audi'
WIDTH, HEIGHT = 1920, 1080
frame = None            # camera frame; not including annotations
client = dict()         # information about the client
features = dict()       # information about the client's desired car
finished = False        # whether the client is finished with the pipeline

def end_all():
    global finished
    finished = True
    app.destroy()
    os._exit(1)

def confirm_exit(event):
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        end_all()

# display front camera
def play_video():
    global frame

    # Capture frame-by-frame
    _, screen = cap.read()
    frame = screen.copy()
    cv2.imwrite('face.jpg', screen)

    try:
        # Find face
        face_objs = DeepFace.extract_faces(img_path = "face.jpg")
        region = face_objs[0]['facial_area']
        x,y,w,h = region['x'], region['y'], region['w'], region['h']
    
        # Draw bounding box
        start = (x,y)
        end = (x+w,y+h)
        cv2.rectangle(screen, start, end, (0, 255, 0), 2)

        # Add annotations
        for i, val in enumerate(client.values()):
            y0 = y - 40*i
            cv2.putText(screen, str(val), (x+w,y0+h), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)
    except:
        pass

    # Display image on the label every 10 ms
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGBA)
    screen = ImageTk.PhotoImage(image=Image.fromarray(screen))
    cam_widget.photo_image = screen
    cam_widget.configure(image=screen)

    # Display the talking message if available
    message = utils.OUTPUT_MESSAGE
    if message is None:
        message_widget.forget()
    if message is not None:
        message_widget.configure(text=message)
        message_widget.configure(width=WIDTH * 2/3)

    # Repeat
    cam_widget.after(10, play_video)

# "Talk" with client
def play_conversation():
    global finished

    TTS(f'Welcome to {DEALERSHIP}. I will be your personal shopping assistant today. I have been programmed by the humans at {DEALERSHIP} to streamline your dealership visit.')
    TTS('My name is JAAID. I am the future of automotive retail. Who do I have the pleasure of meeting today?')

    # Listen for client's name
    client['name'] = STT(duration=2)

    # Continue the conversation to update desired car features:
    TTS('Hello {}. With a few questions, I will activate the \"Autonomous Showroom\", and assemble a {} IQ team that will provide you with human support. Are you looking for a new or used car today?'.format(client['name'], DEALERSHIP))
    response = STT(duration=2)
    features['new'] = True if 'new' in response else False
    TTS('Which model are you interested in seeing today?')
    features['interest'] = STT(duration=3)
    TTS('What vehicle are you comparing the {} to?'.format(features['interest']))
    features['similar'] = STT(duration=3)
    TTS('What vehicle are you replacing?')
    features['current'] = STT(duration=3)

    # Send all info to front desk
    TTS('Thank you. Please wait while I assign you a sales representative to help you.')
    print('\n', '*' * 50, '\n')
    print('Sent to sales representative: ')
    client.update(features)
    print(client)

    con = get_client_connection()
    insert_client(con, client)
    view_clients(con)

    end_all()

# Do the whole client pipeline
def play_pipeline():

    # Delete the previous screen
    frame.destroy()
    message_widget.place(anchor='n', relx=0.5)
    message_widget.tkraise()

    # Start webcam
    t0 = Thread(target=play_video)
    t0.start()

    # Start facial demographics
    t1 = Thread(target=get_facial_info)
    t1.start()

    # Start conversation
    t2 = Thread(target=play_conversation)
    t2.start()

def get_facial_info():
    while(not finished):
        # Predict demographics
        try:
            # print('Getting demographics...')
            dem = DeepFace.analyze(img_path = 'face.jpg',
                actions = ['age', 'gender', 'race', 'emotion'],
                silent=True
            )
        except:
            print('No face detected.')
            continue

        # Save collected facial data to client info
        dem = dem[0]
        client['age']     = dem['age']
        client['male']    = True if dem['dominant_gender']=='Man' else False
        client['race']    = dem['dominant_race']
        client['emotion'] = dem['dominant_emotion']

# Initialize app
app = tk.Tk()
app.title("JAAID")
app.geometry(f'{WIDTH}x{HEIGHT}')
app.bind('<Escape>', confirm_exit) # press Esc to quit

# Initialize camera
cap = cv2.VideoCapture(DEFAULT_CAMERA)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cam_widget = tk.Label(app)
cam_widget.pack()
message_widget = tk.Message(app, font=('Calibri', '40', 'bold'),
                            bg='black', fg='white', width=WIDTH)

# Intro screen
frame = tk.Frame(app)
frame.pack(expand=True, fill=tk.BOTH)

bgimg = ImageTk.PhotoImage(Image.open('images/audi.jpg'))
tk.Label(frame, i=bgimg).place(anchor='center', relx=0.5, rely=0.5)
tk.Label(frame, text='Welcome to the Autonomous Showroom!',
        font=('Calibri', '50', 'bold')).pack()
buttonFont = font.Font(family='Helvetica', size=36)
tk.Button(frame, text="Click to Start", command=play_pipeline, font=buttonFont) \
        .place(anchor='s', relx=0.5, rely=0.9)

app.mainloop()