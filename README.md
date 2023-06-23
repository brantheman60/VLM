# Important Notes about running the Code #

- this code is run in a (Mini)conda environment on Python 3.8.16 on MacBook Air with M2 Chip
- in CLIENT_ID.py, set the DEFAULT_CAMERA and DEALERSHIP variables to suit your needs
- if you have trouble running $ pip install sounddevice, install PortAudio first (???)
- in pyttsx3/drivers/nsss.py, remove the ,attr['VoiceAge'] part of the returned Voice in function _toVoice() in line 64
- if you get an error with recording voice in STT() (MemoryError: Cannot allocate write+execute memory for ffi.callback()), run $ conda install "cffi >= 1.15.1=*_3"
- for Mac M1/M2 users, if you run into "Bad CPU Type" while installing a speech-to-text library, install Rosetta with $ /usr/sbin/softwareupdate -install-rosetta -agree-to-license