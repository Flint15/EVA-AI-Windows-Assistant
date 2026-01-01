import asyncio
import edge_tts
import os
import sounddevice as sd
import librosa
import requests
import pygame  # For MP3 playback
import time
import logging
from timing_decorator import functime
from typing import Optional, Callable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functime
def text_to_speech(
    text, voice_id="kdmDKE6EkgrWrrykO9Qt", api_key='Your ElevenLabs API key', 
    output_file="output.mp3", play_audio=True, 
    stop_stt_callback: Optional[Callable] = None, start_stt_callback: Optional[Callable] = None
    ):
    """
    Convert text to speech using ElevenLabs API and optionally play it.
    
    Args:
        text (str): The text to convert to speech
        voice_id (str): The ElevenLabs voice ID to use
        api_key (str): Your ElevenLabs API key
        output_file (str): The file path to save the audio
        play_audio (bool): Whether to play the audio after saving
        on_tts_start (callable, optional): Callback function called when TTS starts
        on_tts_end (callable, optional): Callback function called when TTS ends
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Call TTS start callback if provided
        if stop_stt_callback:
            stop_stt_callback()
            
        # Build the request endpoint and headers
        TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",  # Request MP3 format
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }

        # Build the JSON payload
        payload = {
            "text": text,
        }

        logger.info(f"Making TTS request to ElevenLabs for text: '{text[:50]}...'")

        # Make the POST request
        response = requests.post(TTS_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Save the audio file
        try:
            with open(output_file, "wb") as f:
                f.write(response.content)
                logger.info(f"Audio saved to {output_file}")
        except IOError as e:
            logger.error(f"Failed to save audio file {output_file}: {e}")
            if start_stt_callback:
                start_stt_callback()
            return False

        # Play the MP3 file if requested
        if play_audio:
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()
                    
                # Wait for the audio to finish playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                logger.info("Audio playback completed successfully")
            except pygame.error as e:
                logger.error(f"Pygame error during audio playback: {e}")
                if start_stt_callback:
                    start_stt_callback()
                return False
            except Exception as e:
                logger.error(f"Unexpected error during audio playback: {e}")
                if start_stt_callback:
                    start_stt_callback()
                return False
            finally:
                try:
                    pygame.mixer.quit()  # Clean up pygame
                except Exception as e:
                    logger.warning(f"Error cleaning up pygame: {e}")

        # Call TTS end callback if provided
        if start_stt_callback:
            start_stt_callback()

        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to ElevenLabs API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
        if start_stt_callback:
            start_stt_callback()
        return False
    except requests.exceptions.Timeout:
        logger.error("Request to ElevenLabs API timed out")
        if start_stt_callback:
            start_stt_callback()
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to ElevenLabs API. Check your internet connection.")
        if start_stt_callback:
            start_stt_callback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error in text_to_speech: {e}")
        if start_stt_callback:
            start_stt_callback()
        return False

def play_audio(text: str, none_object=None, stop_stt_callback: Optional[Callable] = None, start_stt_callback: Optional[Callable] = None):
    """
    Play the audio with given text using Edge TTS.
    
    Args:
        text (str): The text to convert to speech.
        none_object: Unused parameter (kept for compatibility).
        stop_stt_callback (callable, optional): Callback function called when TTS starts
        start_stt_callback (callable, optional): Callback function called when TTS ends
    """
    
    # Call TTS start callback if provided
    if stop_stt_callback:
        stop_stt_callback()
    
    # Use .mp3 extension to reflect the actual file format
    sound_file_name = 'output.mp3'
    
    try:
        # Asynchronous function to generate the MP3 file
        async def main(audio_file_name: str, text: str):
            communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
            await communicate.save(audio_file_name)  # Saves as MP3
        
        # Generate the MP3 file
        asyncio.run(main(sound_file_name, text))
        
        # Load MP3 file with librosa
        data, fs = librosa.load(sound_file_name, sr=None)  # sr=None keeps native sample rate
        
        # Play the audio
        sd.play(data, samplerate=fs)
        sd.wait()  # Wait for playback to finish
        
        # Clean up by deleting the file
        os.remove(sound_file_name)
        
        # Call TTS end callback if provided
        if start_stt_callback:
            start_stt_callback()
            
    except Exception as e:
        logger.error(f"Error in play_audio: {e}")
        # Clean up file if it exists
        if os.path.exists(sound_file_name):
            try:
                os.remove(sound_file_name)
            except:
                pass
        # Call TTS end callback if provided
        if start_stt_callback:
            start_stt_callback()

if __name__ == "__main__":
    try:
        text = input("Type what you want to play - ")
        if text.strip():
            play_audio(text)
        else:
            print("No text provided, exiting.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error in main: {e}")
