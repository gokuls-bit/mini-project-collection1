import re
import webbrowser
import time
import speech_recognition as sr
import pyttsx3

WAKE_WORD = "fig"               # Starter word
ENGINE = pyttsx3.init()         # Text-to-speech for feedback
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()

# Quick command → URL templates
SITE_ALIASES = {
    "youtube":    "https://www.youtube.com",
    "twitter":    "https://twitter.com",
    "twitter x":  "https://twitter.com",
    "x":          "https://twitter.com",
    "github":     "https://github.com",
    "stack overflow": "https://stackoverflow.com"
}

def speak(text: str):
    """Give spoken feedback."""
    ENGINE.say(text)
    ENGINE.runAndWait()

def parse_command(cmd: str):
    """
    Returns ('open', 'site') OR ('search', 'query', 'engine').
    Examples:
        "fig open youtube"      -> ('open', 'youtube')
        "fig search cats"       -> ('search', 'cats', 'google')
        "fig search ai papers on duckduckgo"
                                 -> ('search', 'ai papers', 'duckduckgo')
    """
    cmd = cmd.lower().strip()

    open_match = re.match(rf"{WAKE_WORD}\s+open\s+(.+)", cmd)
    if open_match:
        site_raw = open_match.group(1).strip()
        return ("open", site_raw)

    search_match = re.match(
        rf"{WAKE_WORD}\s+search\s+(.+?)(?:\s+on\s+(google|duckduckgo|bing))?$",
        cmd
    )
    if search_match:
        query = search_match.group(1).strip()
        engine = search_match.group(2) or "google"
        return ("search", query, engine)

    return (None,)

def open_site(site_raw: str):
    """Open a known site alias or assume user gave a URL."""
    site = SITE_ALIASES.get(site_raw, site_raw)
    if not re.match(r"https?://", site):
        site = "https://" + site
    speak(f"Opening {site_raw}")
    webbrowser.open(site)

def search_web(query: str, engine: str):
    ENGINE_URLS = {
        "google":     f"https://www.google.com/search?q={query}",
        "duckduckgo": f"https://duckduckgo.com/?q={query}",
        "bing":       f"https://www.bing.com/search?q={query}",
    }
    speak(f"Searching {query} on {engine}")
    webbrowser.open(ENGINE_URLS[engine])

def listen_loop():
    speak("Voice browser ready. Say fig plus your command.")
    with MIC as source:
        RECOGNIZER.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                print("Listening…")
                audio = RECOGNIZER.listen(source, timeout=5, phrase_time_limit=6)
                transcript = RECOGNIZER.recognize_google(audio)
                print(f"Heard: {transcript}")
                result = parse_command(transcript)
                if result[0] == "open":
                    open_site(result[1])
                elif result[0] == "search":
                    search_web(result[1], result[2])
                else:
                    print("No valid command detected.")
            except sr.WaitTimeoutError:
                # No speech within timeout window – keep listening
                continue
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(0.5)   # Tiny pause before next listen cycle

if __name__ == "__main__":
    listen_loop()