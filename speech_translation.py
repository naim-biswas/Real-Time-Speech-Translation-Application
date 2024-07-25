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
language_mapping = {name.capitalize(): code for code, name in LANGUAGES.items()}

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
        
        with st.spinner("**Listening...**"):
            rec.pause_threshold = 1
            audio = rec.listen(source, phrase_time_limit=10)
    try:
        st.text("Processing...")
        progress_bar = st.progress(0)
        
        spoken_text = rec.recognize_google(audio, language=from_language)
        progress_bar.progress(50)  # Update progress bar to 50%
        
        st.text("Translating...")
        translated_text = translate_text(spoken_text, from_language, to_language)
        progress_bar.progress(100)  # Update progress bar to 100%
        
        text_to_speech(translated_text, to_language)
    
    except Exception as e:
        st.text(f"Error: {e}")

# Streamlit UI setup
#st.title("Real-time Speech Application")
st.markdown(
    """
    <h1 style='text-align: center;'>
    Real-time Speech Application
    </h1>
    """, 
    unsafe_allow_html=True
)

# Dropdown menus for language selection
capitalized_languages = {code: name.capitalize() for code, name in LANGUAGES.items()}
from_language_name = st.selectbox("Select Source Language:", list(capitalized_languages.values()))
to_language_name = st.selectbox("Select Target Language:", list(capitalized_languages.values()))

# Convert language names to codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Buttons to start and stop the translation process
st.markdown("""
    <style>
    .button-container {
        display: flex;
        justify-content: space-between;
    }
    .stButton button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 24px;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 70px;
        cursor: pointer;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

col1, spacer, col2 = st.columns([1, 1, 1])
with col1:
    start_button = st.button("Start")
with col2:
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
