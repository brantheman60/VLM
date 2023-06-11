# Important Notes about running the Code #

- this code is run in a (Mini)conda environment on Python 3.8.16 on MacBook Air with M2 Chip
- in CLIENT_ID.py, set the DEFAULT_CAMERA and DEALERSHIP variables to suit your needs
- in pyttsx3/drivers/nsss.py, remove the ,attr['VoiceAge'] part of the returned Voice in function _toVoice() in line 64
- if you get an error with recording voice in STT() (MemoryError: Cannot allocate write+execute memory for ffi.callback()), run $ conda install "cffi >= 1.15.1=*_3"