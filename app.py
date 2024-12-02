# import pyaudio
# import pyttsx3
# import speech_recognition as sr
# import eel
# import time
# import multiprocessing
# import os
# import pyautogui as autogui
# import openwakeword
# from openwakeword.model import Model
# import numpy as np

# openwakeword.utils.download_models()


# def speak(text):
#     text = str(text)
#     engine = pyttsx3.init()
#     voices = engine.getProperty("voices")
#     engine.setProperty("voice", voices[0].id)
#     engine.setProperty("rate", 125)
#     engine.say(text)
#     engine.runAndWait()


# def chatBot(query):
#     print(query)
#     speak(query)
#     return query


# def takecommand():
#     r = sr.Recognizer()

#     with sr.Microphone() as source:
#         print("listening....")
#         r.pause_threshold = 1
#         r.adjust_for_ambient_noise(source)

#         audio = r.listen(source, 10, 6)

#     try:
#         print("recognizing")
#         query = r.recognize_whisper(audio, model="medium", language="english")
#         print(f"user said: {query}")
#         time.sleep(2)

#     except Exception as e:
#         print("error occured: ", e)
#         return ""

#     return query.lower()


# @eel.expose
# def allCommands(message=1):
#     if message == 1:
#         query = takecommand()
#         print(query)
#         eel.senderText(query)
#     else:
#         query = message
#         eel.senderText(query)
#     try:
#         if "search" in query:
#             query = query.replace("search", "")

#         else:
#             chatBot(query)
#     except Exception as e:
#         print(f"error {e}")

#     eel.ShowHood()


# def hotword():
#     owwModel = None
#     paud = None
#     audio_stream = None

#     try:
#         owwModel = Model(inference_framework="onnx")

#         FORMAT = pyaudio.paInt16
#         CHANNELS = 1
#         RATE = 16000
#         CHUNK = 1280

#         last_detection_time = 0
#         COOLDOWN_PERIOD = 3.0
#         detection_active = False

#         paud = pyaudio.PyAudio()
#         audio_stream = paud.open(
#             format=FORMAT,
#             channels=CHANNELS,
#             rate=RATE,
#             input=True,
#             frames_per_buffer=CHUNK,
#         )

#         print("\nListening for wake words...")
#         print("-" * 50)

#         while True:
#             current_time = time.time()

#             audio_data = np.frombuffer(audio_stream.read(CHUNK), dtype=np.int16)
#             prediction = owwModel.predict(audio_data)

#             for model_name in owwModel.prediction_buffer.keys():
#                 scores = list(owwModel.prediction_buffer[model_name])

#                 if (
#                     scores[-1] > 0.5
#                     and not detection_active
#                     and (current_time - last_detection_time) > COOLDOWN_PERIOD
#                 ):
#                     print(f"Hotword detected! ({model_name})")
#                     detection_active = True
#                     last_detection_time = current_time

#                     autogui.keyDown("win")
#                     autogui.press("j")
#                     time.sleep(0.5)
#                     autogui.keyUp("win")

#                 elif scores[-1] <= 0.3:
#                     detection_active = False

#     except Exception as e:
#         print(f"Error occurred: {e}")

#     finally:
#         if audio_stream is not None:
#             audio_stream.close()
#         if paud is not None:
#             paud.terminate()


# def start():
#     eel.init("web")

#     @eel.expose
#     def init():
#         speak("Hello I am Chakshu")

#     os.system('start msedge.exe --app="http://localhost:8000/index.html"')

#     eel.start("index.html", mode=None, host="localhost", block=True)


# def startChakshu():
#     print("Process 1 is running.")
#     start()


# def listenHotword():
#     print("Process 2 is running.")
#     hotword()


# if __name__ == "__main__":
#     p1 = multiprocessing.Process(target=startChakshu)
#     p2 = multiprocessing.Process(target=listenHotword)
#     p1.start()
#     p2.start()
#     p1.join()

#     if p2.is_alive():
#         p2.terminate()
#         p2.join()

#     print("system stop")


import pyaudio
import pyttsx3
import speech_recognition as sr
import eel
import sys
import time
import multiprocessing
import os
import pyautogui as autogui
import openwakeword
from openwakeword.model import Model
import numpy as np

openwakeword.utils.download_models()


def get_base_dir():
    """Get the base directory for the application."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
        return os.path.join(sys._MEIPASS, "web")
    else:  # Running in development
        return os.path.join(os.path.dirname(__file__), "web")


def speak(text):
    text = str(text)
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 125)
    engine.say(text)
    engine.runAndWait()


def start(stop_event):
    base_dir = get_base_dir()
    eel.init(base_dir)

    @eel.expose
    def init():
        speak("Hello, I am Chakshu")

    # Launch the browser in app mode
    os.system(f'start msedge.exe --app="http://localhost:8000/index.html"')

    try:
        eel.start("index.html", mode=None, host="localhost", block=False)
        # Keep running until the stop_event is set
        while not stop_event.is_set():
            eel.sleep(1)
    except Exception as e:
        print(f"Error in Eel: {e}")
    finally:
        print("Eel process exiting...")
        
def chatBot(query):
    print(query)
    speak(query)
    return query


def listenHotword(stop_event):
    print("Hotword listener started...")
    while not stop_event.is_set():
        print("Listening for hotword...")
        stop_event.wait(5)
    
def takecommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("listening....")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)

        audio = r.listen(source, 10, 6)

    try:
        print("recognizing")
        query = r.recognize_whisper(audio, model="medium", language="english")
        print(f"user said: {query}")
        time.sleep(2)

    except Exception as e:
        print("error occured: ", e)
        return ""

    return query.lower()

@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    try:
        if "search" in query:
            query = query.replace("search", "")

        else:
            chatBot(query)
    except Exception as e:
        print(f"error {e}")

    eel.ShowHood()


def hotword():
    owwModel = None
    paud = None
    audio_stream = None

    try:
        owwModel = Model(inference_framework="onnx")

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1280

        last_detection_time = 0
        COOLDOWN_PERIOD = 3.0
        detection_active = False

        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        print("\nListening for wake words...")
        print("-" * 50)

        while True:
            current_time = time.time()

            audio_data = np.frombuffer(audio_stream.read(CHUNK), dtype=np.int16)
            prediction = owwModel.predict(audio_data)

            for model_name in owwModel.prediction_buffer.keys():
                scores = list(owwModel.prediction_buffer[model_name])

                if (
                    scores[-1] > 0.5
                    and not detection_active
                    and (current_time - last_detection_time) > COOLDOWN_PERIOD
                ):
                    print(f"Hotword detected! ({model_name})")
                    detection_active = True
                    last_detection_time = current_time

                    autogui.keyDown("win")
                    autogui.press("j")
                    time.sleep(0.5)
                    autogui.keyUp("win")

                elif scores[-1] <= 0.3:
                    detection_active = False

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


if __name__ == "__main__":
    multiprocessing.freeze_support()

    stop_event = multiprocessing.Event()

    p1 = multiprocessing.Process(target=start, args=(stop_event,))
    p2 = multiprocessing.Process(target=listenHotword, args=(stop_event,))

    p1.start()
    p2.start()

    try:
        p1.join()
    except KeyboardInterrupt:
        print("Interrupted!")

    stop_event.set()

    if p2.is_alive():
        p2.terminate()
        p2.join()

    print("System stopped.")

