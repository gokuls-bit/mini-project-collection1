import speech_recognition as sr
import pyttsx3
import webbrowser
import musiclib  # Ensure this file contains: music = { "songname": "url", ... }
import requests
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyB3EUbj0TDkLl5ISF4ar6IQl_6R9lbGsrM")
model = genai.GenerativeModel('gemini-pro')

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "7a5aecdd990e498ea8e5982fbb72a965"

def speak(text):
    engine.say(text)
    engine.runAndWait()

def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def processcommand(command):
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
        r = requests.get(
            f"https://newsapi.org/v2/everything?q=tesla&from=2025-05-09&sortBy=publishedAt&apiKey={newsapi}"
        )
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            for article in articles[:5]:
                speak(article['title'])

    elif "play" in command and "music" in command:
        speak("Which song would you like me to play?")
        words = command.split()
        for word in words:
            if word in musiclib.music:
                speak(f"Playing {word}")
                webbrowser.open(musiclib.music[word])
                return
        speak("Sorry, I don't know that song.")

    else:
        # Let Gemini handle unknown commands
        speak("I'm not sure how to handle that. Let me think...")
        response = generate_response(command)
        print("Gemini Response:", response)
        speak(response)

if __name__ == "__main__":
    speak("Initializing Jarvis, please wait...")
    while True:
        print("Recognizing...")
        try:
            with sr.Microphone() as source:
                print("Say something!")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

            word = recognizer.recognize_google(audio)
            if word.lower() == "jarvis":
                speak("Yes, how can I assist you?")
                with sr.Microphone() as source:
                    print("Listening for your command...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processcommand(command)

        except Exception as e:
            print(f"Error: {e}")
