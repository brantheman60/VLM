# System libraries
import os
import time
import sys
from subprocess import call
import utils
from utils import *
from SALES_ID import *
import LEAD_ID
from LEAD_ID import *

# App libraries
import tkinter as tk
from tkinter import messagebox
from tkinter import font

# Multi-threading
from threading import Thread

# Computer Vision Libraries
import cv2
from deepface import DeepFace
from PIL import Image, ImageTk, ImageDraw
# import face_recognition

# DeepFace.stream('client_database')

# Global Variables
DEFAULT_CAMERA = 1      # 0 or 1 for most computers
DEALERSHIP = 'Audi'
# WIDTH, HEIGHT = 1920, 1080
WIDTH, HEIGHT = 1800, 1000
BLANK = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
GREEN = BLANK + np.array([0, 255, 0], dtype=np.uint8)
frame = None            # camera frame; not including annotations
client = dict()         # information about the client
features = dict()       # information about the client's desired car
finished = False        # whether the client is finished with the pipeline

def end_all():
    global finished
    finished = True
    os._exit(1)


def confirm_exit(event):
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        end_all()

# update label widget's screen display (with BGR image)
def update_label_widget(widget, screen):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGBA)
    screen = ImageTk.PhotoImage(image=Image.fromarray(screen))
    widget.image = screen
    widget.configure(image=screen)

def update_button_widget(widget, screen):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGBA)
    screen = ImageTk.PhotoImage(image=Image.fromarray(screen))
    widget.image = screen
    widget.configure(image=screen)

# display front camera
def play_video():
    global frame
    if finished:
        cam_widget.forget()
        return

    # Capture frame-by-frame
    _, screen = cap.read()
    frame = screen.copy()
    cv2.imwrite('face.jpg', screen)

    try:
        # Find face
        face_objs = DeepFace.extract_faces(img_path = "face.jpg")
        region = face_objs[0]['facial_area']
        x,y,w,h = region['x'], region['y'], region['w'], region['h']
    
        # NEW: Add facial features
        # face_landmarks_list = face_recognition.face_landmarks(screen)
        # draw = ImageDraw.Draw(Image.fromarray(screen))
        # for face_landmarks in face_landmarks_list:
        #     for facial_feature in face_landmarks.keys():
        #         draw.line(face_landmarks[facial_feature], width=5, fill=(50, 181, 201))

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

    # Display image on the label
    update_label_widget(cam_widget, screen)

    # Display the talking message if available
    message = utils.OUTPUT_MESSAGE
    if message is None:
        message_widget.forget()
    if message is not None:
        message_widget.configure(text=message)
        message_widget.configure(width=WIDTH * 2/3)

    # Repeat every 1 ms
    cam_widget.after(1, play_video)

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
    features['compare'] = STT(duration=3)
    TTS('What vehicle are you replacing?')
    features['current'] = STT(duration=3)
    
    client.update(features)

    # Finish conversation
    TTS('Thank you. Please wait while I assign you a sales representative to help you.')
    finished = True
    print('\n', '*' * 50, '\n')

    # Send all info to front desk
    con = get_database_connection()
    client_id = insert_table_entry(con, 'clients', client)

    # Get best sales rep for client
    # view_table(con, 'clients')
    # view_table(con, 'sales')
    best_rep = best_sales_rep(con, client_id)
    best_rep_id = best_rep['id']
    print('Best sales rep:', best_rep)

    # Get K best vehicles for client
    K = 3
    df = load_car_data()
    best_trims = best_car_matches(K, client['interest'], client['compare'])
    print('Best trims:', best_trims)

    # Activate the results screen
    results_frame.pack(expand=True, fill=tk.BOTH)
    results_label.pack(expand=True, fill=tk.BOTH)
    message_widget.tkraise()
    tk.Button(results_frame, text="Got it", command=end_all, font=buttonFont) \
        .place(anchor='s', relx=0.5, rely=0.9)

    # Display matched sales rep
    text = 'Your matched sales representative is {}.'.format(best_rep['name'])
    rep_image = cv2.imread(f'sales_database/sales{best_rep_id}.jpg')
    rep_image = resize(rep_image, height=HEIGHT/3)
    screen = pic_in_pic(BLANK, rep_image, x=HEIGHT/2, y=WIDTH/2, center=True)
    update_label_widget(results_label, screen)
    message_widget.configure(text=text)
    TTS(text)

    message_widget.configure(text=text)

    # Display matched vehicles
    text = 'Your best vehicle matches are:\n'
    trim_pics = []
    trim_urls = []
    for i, trim in enumerate(best_trims):
        text += '{}. {}'.format(i+1, trim)
        if i<len(best_trims)-1:
            text += '\n'
        
        trim_url = df.loc[trim]['image']
        trim_pics.append(image_from_url(trim_url)) # each image is 233 x 350
        trim_urls.append(df.loc[trim]['url'])

    
    message_widget.configure(text=text)
    screen = BLANK
    x_arr = [HEIGHT/2] * K
    y_arr = [0.8 * WIDTH*i/K for i in range(K)]
    y_arr = [y + (WIDTH - y_arr[-1]) / 2 for y in y_arr] # center all pics

    screen = pics_in_pic(screen, trim_pics, x_arr, y_arr, center=True)
    update_label_widget(results_label, screen)

    TTS(text)

    

# Do the whole client pipeline
def play_pipeline():

    # Delete the previous screen
    intro_frame.destroy()
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
            # print('No face detected.')
            continue

        # Save collected facial data to client info
        dem = dem[0]
        client['age']     = dem['age']
        client['male']    = True if dem['dominant_gender']=='Man' else False
        client['race']    = dem['dominant_race']
        client['emotion'] = dem['dominant_emotion']

# Initialize app
app = tk.Tk()
jaaid_img = tk.Image("photo", file="images/jaaid.png")
app.tk.call('wm','iconphoto', app._w, jaaid_img)
app.title("JAAID")
app.geometry(f'{WIDTH}x{HEIGHT}')
app.bind('<Escape>', confirm_exit) # press Esc to quit

# Initialize camera screens
cap = cv2.VideoCapture(DEFAULT_CAMERA)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cam_widget = tk.Label(app)
cam_widget.pack()
message_widget = tk.Message(app, font=('Calibri', '40', 'bold'),
                            bg='black', fg='white', width=WIDTH)

# Initialize intro screen
intro_frame = tk.Frame(app)
intro_frame.pack(expand=True, fill=tk.BOTH)

bgimg = ImageTk.PhotoImage(Image.open('images/audi.jpg'))
tk.Label(intro_frame, i=bgimg).place(anchor='center', relx=0.5, rely=0.5)
tk.Label(intro_frame, text='Welcome to the Autonomous Showroom!',
        font=('Calibri', '50', 'bold')).pack()
buttonFont = font.Font(family='Helvetica', size=36)
tk.Button(intro_frame, text="Begin JAAID", command=play_pipeline, font=buttonFont) \
        .place(anchor='s', relx=0.5, rely=0.9)
tk.Button(intro_frame, text="Browse Cars", command=lambda: open_url('https://www.audiusa.com/'), font=buttonFont) \
        .place(anchor='s', relx=0.5, rely=0.8)

# Initialize final results screen
results_frame = tk.Frame(app)
results_label = tk.Label(results_frame)

# app.iconbitmap("images/jaaid.ico")
app.mainloop()
