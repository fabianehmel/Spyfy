print "This line will be printed."
languageCode = "de-DE"
#languageCode = "en-GB"

# NOTE: this requires PyAudio because it uses the Microphone class
import pyaudio
import speech_recognition as sr
print "imported speech_recognition"

r = sr.Recognizer(language = languageCode)
print "initialized recognizer"

with sr.Microphone() as source:                # use the default microphone as the audio source
    print("listening")
    audio = r.listen(source) 2>/dev/null                  # listen for the first phrase and extract it into audio data

try:
    print("You said " + r.recognize(audio))    # recognize speech using Google Speech Recognition
except IndexError:                                  # the API key didn't work
    print("No internet connection")
except KeyError:                                    # the API key didn't work
    print("Invalid API key or quota maxed out")
except LookupError:                            # speech is unintelligible
    print("Could not understand audio")