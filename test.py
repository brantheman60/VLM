# import os
# os.system('say ok')

# import pyttsx3
# tts = pyttsx3.init()

# voices = tts.getProperty('voices')
# for voice in voices:
#     if voice.gender == 'VoiceGenderFemale':
#         print(voice.id, voice.languages[0])
#     # if voice.languages[0] == 'en_US' and voice.gender == 'VoiceGenderFemale':
#     #     print(voice.id, voice.languages[0])

# tts.setProperty('rate', 175)
# tts.setProperty('volume', 1.0)
# tts.setProperty('voice', 'com.apple.voice.compact.en-ZA.Tessa')

# tts.say("I will speak this text")
# tts.runAndWait()

import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("I am listening...")
    audio = r.listen(source)
print(audio)