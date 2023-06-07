import sys
import pyttsx3

def init_engine():
    tts = pyttsx3.init()
    tts.setProperty('rate', 175)
    tts.setProperty('volume', 1.0)
    tts.setProperty('voice', 'com.apple.voice.compact.en-US.Samantha')
    return tts

def say(s):
    tts.say(s)
    tts.runAndWait() #blocks

tts = init_engine()
say(str(sys.argv[1]))