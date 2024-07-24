import os
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

# Global variable to control the translation loop
isTranslateOn = False

# Initialize the translator and sound mixer
translator = Translator()
pygame.mixer.init()

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    """Get the language code from the language name."""
    return language_mapping.get(language_name, language_name)

def translate_text(text, from_language, to_language):
    """Translate text from one language to another."""
    translation = translator.translate(text, src=from_language, dest=to_language)
    return translation.text

def text_to_speech(text, language_code):
    """Convert text to speech and play it."""
    tts = gTTS(text=text, lang=language_code, slow=False)
    tts.save("temp_audio.mp3")
    audio = pygame.mixer.Sound("temp_audio.mp3")
    audio.play()
    os.remove("temp_audio.mp3")  # Remove the temporary audio file

def listen_and_translate(from_language, to_language):
    """Listen to audio, translate it, and play the translation."""
    rec = sr.Recognizer()
    with sr.Microphone() as source:
        st.text("Listening...")
        rec.pause_threshold = 1
        audio = rec.listen(source, phrase_time_limit=10)
    
    try:
        st.text("Processing...")
        spoken_text = rec.recognize_google(audio, language=from_language)
        st.text("Translating...")
        translated_text = translate_text(spoken_text, from_language, to_language)
        text_to_speech(translated_text, to_language)
    
    except Exception as e:
        st.text(f"Error: {e}")  # Display any errors

# Streamlit UI setup
st.title("Real-time Speech Application")

# Dropdown menus for language selection
from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()))
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()))

# Convert language names to codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Buttons to start and stop the translation process
start_button = st.button("Start")
stop_button = st.button("Stop")

# Start translation process when "Start" button is clicked
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        while isTranslateOn:
            listen_and_translate(from_language, to_language)

# Stop translation process when "Stop" button is clicked
if stop_button:
    isTranslateOn = False
