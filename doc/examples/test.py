import pyttsx3

engine = pyttsx3.init()

# voices = engine.getProperty('voices')
# for voice in voices:
#     print(voice)
engine.setProperty("voice","spanish-latin-am")
engine.say("Buenas tardes Facundo")
engine.startLoop()
# engine.runAndWait()