import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator
from streamlit_navigation_bar import st_navbar

# Add a navigation bar to the app

styles = {
    "nav": {
        "background-color": "#655194",
        "display": "flex",
        "justify-content": "center",  # Center horizontally
        "align-items": "center",  # Center vertically
        "height": "60px",
        "width": "100%",  # Ensure the nav bar spans the entire width of the page
        "text-align": "center"  # Center text within the nav bar
    },
    "active": {
        "color": "white",
        "font-weight": "Bold",
        "font-size": "20px",
    }
}

page = st_navbar([" A different language is a different vision of life !!!!!!!"], styles=styles)

# Global variable to control the translation loop
isTranslateOn = False

# Initialize the translator and sound mixer
translator = Translator()
pygame.mixer.init()

# Create a mapping between language names and language codes
language_mapping = {name.capitalize(): code for code, name in LANGUAGES.items()}

# Main content of the app
st.markdown(
    """
    <h1 style='text-align: center; color:#655194; padding-bottom: 30px;'>
        Real-time Speech Translation
    </h1>
    """,
    unsafe_allow_html=True
)

# Get dynamic values from the webpage
# Page layout
col1, col2 = st.columns([0.3, 0.7])

with col1:
    with st.expander("**Settings**", expanded=True):
        pause_threshold = st.slider("Pause Threshold", min_value=0.5, max_value=3.0, value=1.0, step=0.1)
        phrase_time_limit = st.number_input("Phrase Time Limit (seconds)", min_value=1, max_value=60, value=10, step=1)


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


def listen_and_translate(from_language, to_language, status_placeholder, progress_bar, message_placeholder):
    """Listen to audio, translate it, and play the translation."""

    rec = sr.Recognizer()

    with sr.Microphone() as source:
        with st.spinner("Listening..."):
            rec.pause_threshold = pause_threshold
            audio = rec.listen(source, phrase_time_limit=phrase_time_limit)
    try:
        status_placeholder.text("Processing...")
        progress_bar.progress(0)

        spoken_text = rec.recognize_google(audio, language=from_language)
        progress_bar.progress(50)  # Update progress bar to 50%

        status_placeholder.text("Translating...")
        translated_text = translate_text(spoken_text, from_language, to_language)
        progress_bar.progress(100)  # Update progress bar to 100%

        text_to_speech(translated_text, to_language)
        status_placeholder.empty()
        progress_bar.empty()  # Clear the status placeholder after completion

        # Display the translated text as a success message
        message_placeholder.success(f"Translated Text: {translated_text}")
        time.sleep(3)  # Wait for 3 seconds to show the message

    except sr.UnknownValueError:
        message_placeholder.error("Sorry, I could not understand the audio. Please speak clearly and loudly.")
        progress_bar.empty()
        time.sleep(3)
    except sr.RequestError as e:
        message_placeholder.error(f"Error with the speech recognition service: {e}")
        time.sleep(3)
    except Exception as e:
        message_placeholder.error(f"Error during processing or translation: {e}")
        time.sleep(3)
    finally:
        message_placeholder.empty()  # Clear the message after displaying it


# Dropdown menus for language selection
capitalized_languages = {code: name.capitalize() for code, name in LANGUAGES.items()}
with col2:
    with st.expander("**Select Language**", expanded=True):
        from_language_name = st.selectbox("Select Source Language:", list(capitalized_languages.values()))
        to_language_name = st.selectbox("Select Target Language:", list(capitalized_languages.values()))

        # Buttons to start and stop the translation process
        st.markdown("""
            <style>
            .button-container {
                display: flex;
                justify-content: space-between;
            }
            .stButton button {
                background-color: #655194; /* Green */
                color: white;
                padding: 10px 21px;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 70px;
                cursor: pointer;
                border-radius: 4px;
            }
            </style>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            start_button = st.button("Start")
        with col2:
            stop_button = st.button("Stop")

# Convert language names to codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Create placeholders for status and messages
status_placeholder = st.empty()
progress_bar = st.empty()
message_placeholder = st.empty()

# Start translation process when "Start" button is clicked
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        while isTranslateOn:
            # Clear messages before starting the listening process
            status_placeholder.empty()
            progress_bar.empty()
            listen_and_translate(from_language, to_language, status_placeholder, progress_bar, message_placeholder)

# Stop translation process when "Stop" button is clicked
if stop_button:
    isTranslateOn = False

# Add footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 90px; /* Fixed height for the footer */
        background-color: #655194;
        color: white;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .footer a {
        color: white;
        margin: 0 15px;
        text-decoration: none;
    }
    .footer i {
        margin-right: 8px;
    }
    </style>
    <div class="footer">
        <p>© 2024 Real-time Speech Translation Application. All rights reserved.</p>
        <p>
            <a href="https://www.facebook.com" target="_blank">
                <i class="fa fa-facebook"></i> Facebook
            </a>
            <a href="https://www.instagram.com" target="_blank">
                <i class="fa fa-instagram"></i> Instagram
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Include FontAwesome for icons
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    """,
    unsafe_allow_html=True
)
