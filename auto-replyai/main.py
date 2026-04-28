//pip install SpeechRecognition pyttsx3 pyaudio
import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import pyjokes
import os
 
# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set buzzword
BUZZWORD = "radha"

# Configure TTS voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Use female voice (change index if needed)
engine.setProperty('rate', 160)  # Set speech rate

# Speak function
def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Get current time
def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {now}")

# Perform action based on command
def perform_action(command):
    if "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open chrome" in command:
        speak("Opening Chrome")
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        if os.path.exists(chrome_path):
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            webbrowser.get('chrome').open("https://www.google.com")
        else:
            speak("Chrome path not found.")

    elif "open github" in command:
        speak("Opening GitHub")
        webbrowser.open("https://github.com")

    elif "open chatgpt" in command:
        speak("Opening ChatGPT")
        webbrowser.open("https://chat.openai.com")

    elif "what time is it" in command or "tell me the time" in command:
        tell_time()

    elif "tell me a joke" in command or "make me laugh" in command:
        joke = pyjokes.get_joke()
        speak(joke)

    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            speak(f"Searching Google for {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("What should I search?")

    elif "exit" in command or "stop" in command or "bye" in command:
        speak("Goodbye! Have a great day!")
        exit()

    else:
        speak("Sorry, I didn't understand that command.")

# Main function
def listen_and_respond():
    with sr.Microphone() as source:
        speak("Hi, I'm Radha, your assistant. Say my name followed by a command.")
        while True:
            try:
                print("Listening...")
                audio = recognizer.listen(source)
                query = recognizer.recognize_google(audio).lower()
                print("You said:", query)

                if BUZZWORD in query:
                    command = query.replace(BUZZWORD, "").strip()
                    if command:
                        perform_action(command)
                    else:
                        speak("Yes, I am here. What can I do?")
            except sr.UnknownValueError:
                print("Didn't catch that.")
            except sr.RequestError:
                speak("Could not connect to the speech service.")

# Entry point
if __name__ == "__main__":
    listen_and_respond()
