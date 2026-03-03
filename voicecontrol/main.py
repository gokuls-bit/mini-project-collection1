import re
import webbrowser
import time
import speech_recognition as sr
import pyttsx3
import datetime
import pyjokes
import urllib.parse
import threading
import os
import wikipedia
import json

WAKE_WORD = "fig"
MEMORY_FILE = "assistant_memory.json"

ENGINE = pyttsx3.init()
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()

ENGINE.setProperty("rate", 175)

# -------------------------
# Memory System
# -------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

MEMORY = load_memory()

# -------------------------
# Speak (Non-blocking)
# -------------------------
def speak(text):
    def run():
        print("Assistant:", text)
        ENGINE.say(text)
        ENGINE.runAndWait()

    threading.Thread(target=run).start()

# -------------------------
# Command Parsing
# -------------------------
def parse_command(cmd):
    cmd = cmd.lower().strip()

    if WAKE_WORD not in cmd:
        return None

    cmd = cmd.replace(WAKE_WORD, "", 1).strip()

    if "exit" in cmd or "shutdown assistant" in cmd:
        return ("exit",)

    if cmd.startswith("open"):
        return ("open", cmd.replace("open", "", 1).strip())

    if cmd.startswith("search"):
        return ("search", cmd.replace("search", "", 1).strip())

    if "joke" in cmd:
        return ("joke",)

    if "time" in cmd:
        return ("time",)

    if "weather" in cmd:
        return ("weather",)

    if "who is" in cmd or "what is" in cmd:
        return ("wiki", cmd)

    if "my name is" in cmd:
        return ("remember_name", cmd.replace("my name is", "").strip())

    if "what is my name" in cmd:
        return ("recall_name",)

    if "shutdown computer" in cmd:
        return ("shutdown_pc",)

    if "restart computer" in cmd:
        return ("restart_pc",)

    return ("fallback", cmd)

# -------------------------
# Features
# -------------------------
def open_site(site):
    if not site.startswith("http"):
        site = "https://" + site
    speak(f"Opening {site}")
    webbrowser.open(site)

def search_web(query):
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}"
    speak(f"Searching for {query}")
    webbrowser.open(url)

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")

def tell_joke():
    speak(pyjokes.get_joke())

def show_weather():
    speak("Opening weather report.")
    webbrowser.open("https://www.google.com/search?q=weather+today")

def wikipedia_search(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except:
        speak("Sorry, I couldn't find anything.")

def remember_name(name):
    MEMORY["name"] = name
    save_memory(MEMORY)
    speak(f"Nice to meet you {name}. I will remember that.")

def recall_name():
    name = MEMORY.get("name")
    if name:
        speak(f"Your name is {name}.")
    else:
        speak("I don't know your name yet.")

def shutdown_pc():
    speak("Shutting down the computer.")
    os.system("shutdown /s /t 1")

def restart_pc():
    speak("Restarting the computer.")
    os.system("shutdown /r /t 1")

# -------------------------
# Main Loop
# -------------------------
def listen_loop():
    speak("Advanced voice assistant is ready.")

    with MIC as source:
        RECOGNIZER.adjust_for_ambient_noise(source)

        while True:
            try:
                print("Listening...")
                audio = RECOGNIZER.listen(source, timeout=5, phrase_time_limit=7)
                transcript = RECOGNIZER.recognize_google(audio)
                print("Heard:", transcript)

                result = parse_command(transcript)

                if result is None:
                    continue

                match result:
                    case ("open", site):
                        open_site(site)
                    case ("search", query):
                        search_web(query)
                    case ("joke",):
                        tell_joke()
                    case ("time",):
                        tell_time()
                    case ("weather",):
                        show_weather()
                    case ("wiki", query):
                        wikipedia_search(query)
                    case ("remember_name", name):
                        remember_name(name)
                    case ("recall_name",):
                        recall_name()
                    case ("shutdown_pc",):
                        shutdown_pc()
                    case ("restart_pc",):
                        restart_pc()
                    case ("exit",):
                        speak("Goodbye.")
                        break
                    case ("fallback", query):
                        search_web(query)

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Didn't understand.")
            except Exception as e:
                print("Error:", e)
                speak("Something went wrong.")

            time.sleep(0.5)

if __name__ == "__main__":
    listen_loop()
