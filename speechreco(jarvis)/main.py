import speech_recognition as sr
import pyttsx3
import webbrowser

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    speak("Initializing Jarvis, please wait...")
    while True:
        r = sr.Recognizer()
       
        # recognize speech using Google Cloud (you had recognize_google_cloud)
        print("recognizing....")
        try:
            with sr.Microphone() as source:
                print("Say something!")
                audio = r.listen(source, timeout=3, phrase_time_limit=1)
            
            command = r.recognize_google_cloud(audio)
            if(command.lower()=="jarvis"):
                speak("Yes, how can I assist you?")
                
        except Exception as e:
            print(" error; {0}".format(e))
