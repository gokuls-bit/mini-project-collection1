"""main.py – Jarvis Speech Assistant (API keys now loaded from .env)
---------------------------------------------------------------
• Requires: python-dotenv, SpeechRecognition, pyttsx3, requests, google‑generativeai
• Add the following to a `.env` file **never committed to Git**:
    GEMINI_API_KEY=your_gemini_key_here
    NEWS_API_KEY=your_newsapi_key_here

Optionally (for client.py):
    OPENAI_API_KEY=your_openai_key_here
"""

import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
import musiclib  # music = {"songname": "url", ...}
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Environment & API keys
# ---------------------------------------------------------------------------
load_dotenv()                        # Loads variables from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not GEMINI_API_KEY or not NEWS_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY or NEWS_API_KEY in environment")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ---------------------------------------------------------------------------
# Text‑to‑speech & speech‑to‑text setup
# ---------------------------------------------------------------------------
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text: str) -> None:
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def generate_response(prompt: str) -> str:
    """Use Gemini to generate a natural‑language reply."""
    response = model.generate_content(prompt)
    return response.text

# ---------------------------------------------------------------------------
# Command handling
# ---------------------------------------------------------------------------

def fetch_news() -> None:
    """Read aloud the latest Tesla‑related headlines (top 5)."""
    url = (
        "https://newsapi.org/v2/everything?"  # NewsAPI endpoint
        "q=tesla&sortBy=publishedAt&"          # query + sort
        f"apiKey={NEWS_API_KEY}"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])[:5]
        if not articles:
            speak("I couldn't find any Tesla news at the moment.")
            return
        for article in articles:
            speak(article["title"])
    except Exception as exc:
        speak(f"Sorry, I couldn't reach the news service: {exc}")


def play_music(command: str) -> None:
    """Attempt to play a requested song from musiclib.music."""
    words = command.split()
    for word in words:
        if word in musiclib.music:
            speak(f"Playing {word}")
            webbrowser.open(musiclib.music[word])
            return
    speak("Sorry, I don't know that song.")


def process_command(command: str) -> None:
    """Main command router."""
    command = command.lower()

    if "open google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google")

    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")

    elif "open linkedin" in command:
        webbrowser.open("https://www.linkedin.com/in/gokulkumarsant/")
        speak("Opening your LinkedIn profile")

    elif "open github" in command:
        webbrowser.open("https://github.com/gokuls-bit/")
        speak("Opening your GitHub")

    elif "open email" in command or "open gmail" in command:
        webbrowser.open("https://mail.google.com/")
        speak("Opening Gmail")

    elif "open myntra" in command:
        webbrowser.open("https://www.myntra.com")
        speak("Opening Myntra")

    elif "what is your name" in command:
        speak("I am Jarvis, your personal assistant.")

    elif "how are you" in command:
        speak("I am Jarvis, I am fine.")

    elif "tell me the news" in command:
        fetch_news()

    elif "play" in command and "music" in command:
        play_music(command)

    else:
        speak("I'm not sure how to handle that. Let me think…")
        response = generate_response(command)
        print("Gemini Response:", response)
        speak(response)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    speak("Initializing Jarvis, please wait…")
    while True:
        print("Recognizing…")
        try:
            with sr.Microphone() as source:
                print("Say something!")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

            word = recognizer.recognize_google(audio)
            if word.lower() == "jarvis":
                speak("Yes, how can I assist you?")
                with sr.Microphone() as source:
                    print("Listening for your command…")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    process_command(command)

        except Exception as e:
            print(f"Error: {e}")
