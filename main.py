import speech_recognition as sr
import pyttsx3
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import threading

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Path to the Vosk model
model_path = "./model"  # Change this to the path of your Vosk model

# Load the Vosk model
model = Model(model_path)

# Queue to hold audio data
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# Function to recognize speech using Vosk
def recognize_speech():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Listening...")
        rec = KaldiRecognizer(model, 16000)
        partial_text = ""
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                text = json.loads(result)["text"]
                if "stop listening" in text.lower():
                    print("\nStopping the transcription...")
                    tts_engine.say("Stopping the transcription.")
                    tts_engine.runAndWait()
                    break
                partial_text += " " + text
                print(f"\rRecognized: {partial_text.strip()}", end='', flush=True)
            else:
                partial_result = rec.PartialResult()
                text = json.loads(partial_result)["partial"]
                print(f"\rRecognized: {partial_text} {text}", end='', flush=True)

# Run the recognition in a separate thread
recognition_thread = threading.Thread(target=recognize_speech)
recognition_thread.start()

# Main loop for continuous recognition
try:
    recognition_thread.join()
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"An error occurred: {e}")
