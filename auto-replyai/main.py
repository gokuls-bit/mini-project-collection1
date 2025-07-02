//pip install SpeechRecognition pyttsx3 pyaudio
import speech_recognition as sr
import pyttsx3
import webbrowser

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set buzzword
BUZZWORD = "radha"

# Function to speak
def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Define actions
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
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get('chrome').open("https://www.google.com")
    elif "open github" in command:
        speak("Opening GitHub")
        webbrowser.open("https://github.com")
    else:
        speak("Sorry, I didn't understand the command.")

# Main function
def listen_and_respond():
    with sr.Microphone() as source:
        speak("Assistant is listening. Say 'Radha' followed by a command.")
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
                        speak("Yes, I am here.")
            except sr.UnknownValueError:
                print("Didn't catch that.")
            except sr.RequestError:
                print("Could not request results; check your network.")

# Run
if __name__ == "__main__":
    listen_and_respond()
