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

# =========================
# CONFIGURATION
# =========================

WAKE_WORD = "nova"
MEMORY_FILE = "assistant_memory.json"

ENGINE = pyttsx3.init()
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()

ENGINE.setProperty("rate", 175)

# =========================
# MEMORY SYSTEM
# =========================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

MEMORY = load_memory()

# =========================
# SPEAK FUNCTION (NON-BLOCKING)
# =========================

def speak(text):
    def run():
        print("NOVA:", text)
        ENGINE.say(text)
        ENGINE.runAndWait()

    threading.Thread(target=run).start()

# =========================
# COMMAND PARSER
# =========================

def parse_command(cmd):

    cmd = cmd.lower().strip()

    if WAKE_WORD not in cmd:
        return None

    cmd = cmd.replace(WAKE_WORD, "", 1).strip()

    if "exit" in cmd:
        return ("exit",)

    if "open youtube" in cmd:
        return ("youtube",)

    if "open google" in cmd:
        return ("google",)

    if cmd.startswith("open"):
        return ("open", cmd.replace("open", "", 1).strip())

    if cmd.startswith("search"):
        return ("search", cmd.replace("search", "", 1).strip())

    if "play music" in cmd:
        return ("music",)

    if "system info" in cmd:
        return ("system",)

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

# =========================
# FEATURES
# =========================

def open_site(site):
    if not site.startswith("http"):
        site = "https://" + site
    speak(f"Opening {site}")
    webbrowser.open(site)

def open_youtube():
    speak("Opening YouTube")
    webbrowser.open("https://youtube.com")

def open_google():
    speak("Opening Google")
    webbrowser.open("https://google.com")

def play_music():
    speak("Playing music")
    os.system("start wmplayer")

def system_info():
    speak("Opening system information")
    os.system("systeminfo")

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
    speak("Opening weather report")
    webbrowser.open("https://www.google.com/search?q=weather+today")

def wikipedia_search(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except:
        speak("Sorry, I could not find anything")

def remember_name(name):
    MEMORY["name"] = name
    save_memory(MEMORY)
    speak(f"Nice to meet you {name}. I will remember that")

def recall_name():
    name = MEMORY.get("name")
    if name:
        speak(f"Your name is {name}")
    else:
        speak("I do not know your name yet")

def shutdown_pc():
    speak("Shutting down the computer")
    os.system("shutdown /s /t 1")

def restart_pc():
    speak("Restarting the computer")
    os.system("shutdown /r /t 1")

# =========================
# GREETING SYSTEM
# =========================

def greet_user():

    hour = datetime.datetime.now().hour

    if hour < 12:
        speak("Good morning. Nova AI is online.")

    elif hour < 18:
        speak("Good afternoon. Nova AI is ready.")

    else:
        speak("Good evening. Nova AI at your service.")

# =========================
# MAIN LOOP
# =========================

def listen_loop():

    greet_user()

    with MIC as source:

        RECOGNIZER.adjust_for_ambient_noise(source)

        while True:

            try:

                print("Listening...")
                audio = RECOGNIZER.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=7
                )

                transcript = RECOGNIZER.recognize_google(audio)
                print("Heard:", transcript)

                result = parse_command(transcript)

                if result is None:
                    continue

                match result:

                    case ("open", site):
                        open_site(site)

                    case ("youtube",):
                        open_youtube()

                    case ("google",):
                        open_google()

                    case ("music",):
                        play_music()

                    case ("system",):
                        system_info()

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

                    case ("fallback", query):
                        search_web(query)

                    case ("exit",):
                        speak("Goodbye. Nova shutting down.")
                        break

            except sr.WaitTimeoutError:
                continue

            except sr.UnknownValueError:
                print("Didn't understand")

            except Exception as e:
                print("Error:", e)
                speak("Something went wrong")

            time.sleep(0.5)

# =========================
# START PROGRAM
# =========================

if __name__ == "__main__":
    listen_loop()
