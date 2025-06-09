"""main.py – Jarvis Speech Assistant (Gemini‑powered Q&A fallback)
------------------------------------------------------------------
• Requires: python-dotenv, SpeechRecognition, pyttsx3, requests, google‑generativeai
• Add the following to a `.env` file **never committed to Git**:
    GEMINI_API_KEY=your_gemini_key_here
    NEWS_API_KEY=your_newsapi_key_here

Optionally (for client.py):
    OPENAI_API_KEY=your_openai_key_here
"""

from __future__ import annotations

import os
import re
import sys
import logging
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
import musiclib  # expects: music = {"songname": "url", ...}
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Logging & constants
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

WAKE_WORD = "jarvis"
QUESTION_WORDS = ("what", "who", "when", "where", "why", "how", "which")

# ---------------------------------------------------------------------------
# Environment & API keys
# ---------------------------------------------------------------------------
load_dotenv()  # Loads variables from .env sitting next to this file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not GEMINI_API_KEY or not NEWS_API_KEY:
    logging.error("Missing GEMINI_API_KEY or NEWS_API_KEY in environment. Exiting.")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ---------------------------------------------------------------------------
# Text‑to‑speech & speech‑to‑text setup
# ---------------------------------------------------------------------------
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 175)  # Slightly slower pace for clarity


def speak(text: str) -> None:
    """Convert text to speech (non‑blocking)."""
    logging.info("Assistant → %s", text)
    engine.say(text)
    engine.runAndWait()


# ---------------------------------------------------------------------------
# Gemini helper
# ---------------------------------------------------------------------------

def generate_response(prompt: str) -> str:
    """Use Gemini to generate a concise natural‑language reply."""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logging.exception("Gemini API error: %s", exc)
        return "Sorry, I'm having trouble reaching Gemini right now."


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def is_question(utterance: str) -> bool:
    """Return True if the utterance looks like a question."""
    utterance = utterance.lower().strip()
    return utterance.endswith("?") or utterance.split(" ")[0] in QUESTION_WORDS


# ---------------------------------------------------------------------------
# Command handling
# ---------------------------------------------------------------------------

def fetch_news() -> None:
    """Read aloud the latest Tesla‑related headlines (top 5)."""
    url = (
        "https://newsapi.org/v2/everything?"  # NewsAPI endpoint
        "q=tesla&sortBy=publishedAt&"  # query + sort
        f"apiKey={NEWS_API_KEY}"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])[:5]
        if not articles:
            speak("I couldn't find any Tesla news at the moment.")
            return
        speak("Here are the latest Tesla headlines:")
        for art in articles:
            speak(art["title"])
    except Exception as exc:
        speak(f"Sorry, I couldn't reach the news service: {exc}")


def play_music(command: str) -> None:
    """Attempt to play a requested song from musiclib.music."""
    words = re.findall(r"[\w']+", command.lower())
    for word in words:
        if word in musiclib.music:
            speak(f"Playing {word}")
            webbrowser.open(musiclib.music[word])
            return
    speak("Sorry, I don't know that song.")


# Mapping of command patterns ➜ action callables
COMMANDS: list[tuple[re.Pattern[str], Callable[[str], None]]] = [
    (re.compile(r"\bopen (google)\b"), lambda _: (webbrowser.open("https://www.google.com"), speak("Opening Google"))),
    (re.compile(r"\bopen (youtube)\b"), lambda _: (webbrowser.open("https://www.youtube.com"), speak("Opening YouTube"))),
    (re.compile(r"\bopen (linkedin)\b"), lambda _: (webbrowser.open("https://www.linkedin.com/in/gokulkumarsant/"), speak("Opening your LinkedIn profile"))),
    (re.compile(r"\bopen (github)\b"), lambda _: (webbrowser.open("https://github.com/gokuls-bit/"), speak("Opening your GitHub"))),
    (re.compile(r"\bopen (email|gmail)\b"), lambda _: (webbrowser.open("https://mail.google.com/"), speak("Opening Gmail"))),
    (re.compile(r"\bopen (myntra)\b"), lambda _: (webbrowser.open("https://www.myntra.com"), speak("Opening Myntra"))),
    (re.compile(r"\bwhat is your name\b"), lambda _: speak("I am Jarvis, your personal assistant.")),
    (re.compile(r"\bhow are you\b"), lambda _: speak("I am Jarvis, I am fine.")),
    (re.compile(r"\btell me the news\b"), lambda _: fetch_news()),
    (re.compile(r"\bplay .* music\b"), play_music),  # play <song> music
]


def process_command(command: str) -> bool:
    """Try executing a known command. Returns True if handled."""
    cmd_lower = command.lower()
    for pattern, action in COMMANDS:
        if pattern.search(cmd_lower):
            action(command)  # pass the raw command in case the action needs it
            return True
    return False  # Not handled


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def listen_for_audio(prompt: str | None = None, timeout: int = 5, limit: int = 4) -> str | None:
    """Capture microphone input and convert to text. Returns None on failure."""
    if prompt:
        speak(prompt)
    with sr.Microphone() as source:
        logging.info("Listening…")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=limit)
            transcript = recognizer.recognize_google(audio)
            logging.info("Heard: %s", transcript)
            return transcript
        except Exception as exc:
            logging.warning("Speech recognition error: %s", exc)
            return None


def main() -> None:  # pragma: no cover
    speak("Initializing Jarvis, please wait…")

    while True:
        wake = listen_for_audio(timeout=10, limit=2)
        if wake and wake.lower() == WAKE_WORD:
            command = listen_for_audio("Yes, how can I assist you?", timeout=6, limit=6)
            if not command:
                continue

            # 1️⃣ First try explicit commands
            if process_command(command):
                continue

            # 2️⃣ If it's a question, ask Gemini
            if is_question(command):
                speak("Let me check that for you…")
                answer = generate_response(command)
                speak(answer)
                continue

            # 3️⃣ Fallback: ask Gemini for a suggestion what user might mean
            speak("I'm not sure how to handle that. Let me think…")
            answer = generate_response(
                f"A user said: '{command}'. They asked their voice assistant to interpret it. "
                "Suggest a helpful, friendly response."  # prompt engineering
            )
            speak(answer)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye!")
