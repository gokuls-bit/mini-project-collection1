import re
import webbrowser
import time
import speech_recognition as sr
import pyttsx3
import datetime
import pyjokes

WAKE_WORD = "fig"
ENGINE = pyttsx3.init()
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()

# Voice settings
ENGINE.setProperty("rate", 165)
voices = ENGINE.getProperty("voices")
ENGINE.setProperty("voice", voices[1].id)  # Female voice (optional)

# Known websites
SITE_ALIASES = {
    "youtube":        "https://www.youtube.com",
    "twitter":        "https://twitter.com",
    "x":              "https://twitter.com",
    "github":         "https://github.com",
    "stackoverflow":  "https://stackoverflow.com",
    "chatgpt":        "https://chat.openai.com",
    "linkedin":       "https://www.linkedin.com",
    "gmail":          "https://mail.google.com",
    "google":         "https://www.google.com",
    "reddit":         "https://www.reddit.com"
}

def speak(text: str):
    print("Assistant:", text)
    ENGINE.say(text)
    ENGINE.runAndWait()

def parse_command(cmd: str):
    cmd = cmd.lower().strip()

    if f"{WAKE_WORD} open" in cmd:
        match = re.match(rf"{WAKE_WORD}\s+open\s+(.+)", cmd)
        if match:
            return ("open", match.group(1).strip())

    elif f"{WAKE_WORD} search" in cmd:
        match = re.match(
            rf"{WAKE_WORD}\s+search\s+(.+?)(?:\s+on\s+(google|duckduckgo|bing))?$",
            cmd
        )
        if match:
            query = match.group(1).strip()
            engine = match.group(2) or "google"
            return ("search", query, engine)

    elif f"{WAKE_WORD} joke" in cmd:
        return ("joke",)

    elif f"{WAKE_WORD} time" in cmd:
        return ("time",)

    elif f"{WAKE_WORD} weather" in cmd:
        return ("weather",)

    return (None,)

def open_site(site_raw: str):
    site = SITE_ALIASES.get(site_raw, site_raw)
    if not re.match(r"https?://", site):
        site = "https://" + site
    speak(f"Opening {site_raw}")
    webbrowser.open(site)

def search_web(query: str, engine: str):
    url_map = {
        "google":     f"https://www.google.com/search?q={query}",
        "duckduckgo": f"https://duckduckgo.com/?q={query}",
        "bing":       f"https://www.bing.com/search?q={query}",
    }
    speak(f"Searching for {query} on {engine}")
    webbrowser.open(url_map.get(engine, url_map["google"]))

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def show_weather():
    speak("Weather functionality is not added yet. But it's sunny in my heart.")

def listen_loop():
    speak("Voice browser is ready. Say 'fig' followed by your command.")
    with MIC as source:
        RECOGNIZER.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                print("Listening…")
                audio = RECOGNIZER.listen(source, timeout=5, phrase_time_limit=6)
                transcript = RECOGNIZER.recognize_google(audio)
                print(f"Heard: {transcript}")
                result = parse_command(transcript)

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
                    case _:
                        speak("Sorry, I didn't understand that.")
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except Exception as e:
                print(f"Error: {e}")
                speak("Something went wrong.")
            time.sleep(0.5)

if __name__ == "__main__":
    listen_loop()
