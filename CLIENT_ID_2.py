import tkinter as tk
import cv2
from PIL import Image, ImageTk
from threading import Thread
import time
  
# Define a video capture object
cap = cv2.VideoCapture(1)
  
# Set the width and height of the frame
WIDTH, HEIGHT = 1920, 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
  
# Create a GUI app
app = tk.Tk()
  
# Bind the app with Escape keyboard to
# quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())
  
# Create a label and display it on app
label_widget = tk.Label(app)
label_widget.pack()
  
# Create a function to open camera and
# display it in the label_widget on app
def foo():
    while True:
        print('Hello!')
        time.sleep(1)

def open_camera_thread():
    t0 = Thread(target=open_camera)
    t0.start()
def open_camera():
  
    # Capture the video frame by frame
    _, frame = cap.read()
  
    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
  
    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)
  
    # Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)
  
    # Displaying photoimage in the label
    label_widget.photo_image = photo_image
  
    # Configure image in the label
    label_widget.configure(image=photo_image)
  
    # Repeat the same process after every 10 ms
    label_widget.after(10, open_camera)

# Create a button to open the camera in GUI app
button1 = tk.Button(app, text="Open Camera", command=foo)
# button1.bind('<Button-1>', lambda e: open_camera_thread())
button1.pack()
  
# Create an infinite loop for displaying app on screen
app.mainloop()