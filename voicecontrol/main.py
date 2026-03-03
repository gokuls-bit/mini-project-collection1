import re
import webbrowser
import time
import speech_recognition as sr
import pyttsx3
import datetime
import pyjokes
import urllib.parse

WAKE_WORD = "fig"
EXIT_WORDS = ["exit", "quit", "stop", "shutdown"]

ENGINE = pyttsx3.init()
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()

# ------------------------
# Voice Settings
# ------------------------
ENGINE.setProperty("rate", 170)

voices = ENGINE.getProperty("voices")
if len(voices) > 1:
    ENGINE.setProperty("voice", voices[1].id)

# ------------------------
# Known Websites
# ------------------------
SITE_ALIASES = {
    "youtube": "https://www.youtube.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "linkedin": "https://www.linkedin.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "reddit": "https://www.reddit.com"
}

# ------------------------
# Speak Function
# ------------------------
def speak(text: str):
    print("Assistant:", text)
    ENGINE.say(text)
    ENGINE.runAndWait()

# ------------------------
# Command Parsing
# ------------------------
def parse_command(cmd: str):
    cmd = cmd.lower().strip()

    if not cmd.startswith(WAKE_WORD):
        return None

    cmd = cmd.replace(WAKE_WORD, "", 1).strip()

    if any(word in cmd for word in EXIT_WORDS):
        return ("exit",)

    if cmd.startswith("open"):
        return ("open", cmd.replace("open", "", 1).strip())

    if cmd.startswith("search"):
        match = re.match(r"search\s+(.+?)(?:\s+on\s+(google|duckduckgo|bing))?$", cmd)
        if match:
            query = match.group(1)
            engine = match.group(2) or "google"
            return ("search", query, engine)

    if "joke" in cmd:
        return ("joke",)

    if "time" in cmd:
        return ("time",)

    if "weather" in cmd:
        return ("weather",)

    if "help" in cmd:
        return ("help",)

    return None

# ------------------------
# Features
# ------------------------
def open_site(site_raw: str):
    site_raw = site_raw.strip()

    if site_raw in SITE_ALIASES:
        url = SITE_ALIASES[site_raw]
    else:
        if not site_raw.startswith("http"):
            site_raw = "https://" + site_raw
        url = site_raw

    speak(f"Opening {site_raw}")
    webbrowser.open(url)

def search_web(query: str, engine: str):
    encoded_query = urllib.parse.quote(query)

    url_map = {
        "google": f"https://www.google.com/search?q={encoded_query}",
        "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}",
        "bing": f"https://www.bing.com/search?q={encoded_query}",
    }

    speak(f"Searching for {query} on {engine}")
    webbrowser.open(url_map.get(engine, url_map["google"]))

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")

def tell_joke():
    speak(pyjokes.get_joke())

def show_weather():
    speak("Opening weather details for you.")
    webbrowser.open("https://www.google.com/search?q=weather+today")

def show_help():
    speak("You can say: fig open youtube, fig search AI on google, fig joke, fig time, fig weather, or fig exit.")

# ------------------------
# Listening Loop
# ------------------------
def listen_loop():
    speak("Voice assistant is ready. Say fig followed by your command.")

    with MIC as source:
        RECOGNIZER.adjust_for_ambient_noise(source, duration=1)

        while True:
            try:
                print("Listening...")
                audio = RECOGNIZER.listen(source, timeout=5, phrase_time_limit=6)
                transcript = RECOGNIZER.recognize_google(audio)
                print("Heard:", transcript)

                result = parse_command(transcript)

                if result is None:
                    continue

                match result:
                    case ("open", site):
                        open_site(site)
                    case ("search", query, engine):
                        search_web(query, engine)
                    case ("joke",):
                        tell_joke()
                    case ("time",):
                        tell_time()
                    case ("weather",):
                        show_weather()
                    case ("help",):
                        show_help()
                    case ("exit",):
                        speak("Shutting down. Goodbye.")
                        break
                    case _:
                        speak("Sorry, I didn't understand that.")

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except Exception as e:
                print("Error:", e)
                speak("Something went wrong.")
            
            time.sleep(0.5)

# ------------------------
if __name__ == "__main__":
    listen_loop()
