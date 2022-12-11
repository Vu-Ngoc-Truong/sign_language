#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import playsound
from gtts import gTTS
# import time
# import sys
# import wikipedia
# wikipedia.set_lang('vi')


def text_to_speech(text, language='vi', save_sound=False):
    output = gTTS(text,lang=language, slow=False)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    output.save(dir_path + "/output.mp3")
    playsound.playsound(dir_path + '/output.mp3', True)
    if not save_sound:
        os.remove(dir_path + "/output.mp3")

if __name__ == '__main__':
    # text_to_speech("Xin chào!")
    text_to_speech("Xin chào!", save_sound=True)