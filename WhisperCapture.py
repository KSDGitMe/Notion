from openai import OpenAI
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import keyboard  # For listening to key presses
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv("Journal.env")
api_key = os.getenv('OPENAI_API_KEY')

# Instantiate the OpenAI client
client = OpenAI(api_key=api_key)

SAMPLE_RATE = 16000  # Whisper API accepts 16kHz audio
recording = False

# Function to start recording audio until a key is pressed
def record_audio(sample_rate=SAMPLE_RATE):
    global recording
    recording = True
    audio_data = []

    print("Recording... Press 'spacebar' to stop.")

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    # Start recording, non-blocking mode
    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback, dtype=np.int16):
        while recording:
            if keyboard.is_pressed('space'):
                print("Recording stopped.")
                recording = False
            sd.sleep(100)  # Wait 100ms and check if the spacebar is pressed

    audio_data = np.concatenate(audio_data, axis=0)
    return audio_data

# Function to save the recorded audio to a temporary file
def save_audio_to_file(audio_data, sample_rate=SAMPLE_RATE):
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write(temp_file.name, sample_rate, audio_data)
    return temp_file.name

# Whisper API to convert real-time audio to text using the correct OpenAI client instantiation and method
def transcribe_audio_to_text(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        # Correct use of the client and transcription method
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

# Function to test Whisper API and print transcription
def test_whisper_transcription():
    # Step 1: Record the audio in real-time, manually triggered
    audio_data = record_audio()

    # Step 2: Save the audio data to a temporary file
    audio_file_path = save_audio_to_file(audio_data)

    # Step 3: Transcribe the audio using Whisper API
    text = transcribe_audio_to_text(audio_file_path)

    # Step 4: Print the transcribed text to the console
    print(f"Transcribed Text: {text}")

# Example usage
if __name__ == "__main__":
    test_whisper_transcription()
    