from PyQt5.QtCore import pyqtSignal, QObject
import speech_recognition as sr
import logging
import time
import sys

class SpeechToText(QObject):
    stt_detected_input = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_speech_recognition(self, callback_function=None):
        """
        Start speech recognition in the background.
        
        Args:
            callback_function (callable, optional): A function to be called when speech is detected.
                The function should accept two parameters: (recognizer, audio)
        
        Returns:
            callable: A function to stop the speech recognition
            
        Raises:
            RuntimeError: If microphone initialization fails
        """
        try:
            # Create a Recognizer and Microphone instance
            r = sr.Recognizer()
            mic = sr.Microphone()
                
        except Exception as e:
            error_msg = f"Failed to initialize microphone: {str(e)}"
            self.logger.error(error_msg)

        def default_callback(recognizer, audio):
            try:
                # Use Google's free Web Speech API (requires internet)
                text = recognizer.recognize_google(audio)
                self.logger.info(f"User said: {text}")
                
                if "eva" in text.lower():
                    # Remove 'eva' from the text
                    cleaned_text = text.lower().replace("eva", "").strip()
                    self.stt_detected_input.emit(cleaned_text)

            except sr.UnknownValueError:
                self.logger.debug("Could not understand audio")
            except sr.RequestError as e:
                self.logger.error(f"API error: {e}")
            except OSError as e:
                if "Unanticipated host error" in str(e) or "Stream closed" in str(e):
                    self.logger.warning("Microphone appears to be turned off or disconnected. Please check your microphone connection.")
                else:
                    self.logger.error(f"Microphone error: {str(e)}")
            except Exception as e:
                self.logger.error(f"Unexpected error during speech recognition: {str(e)}")

        # Use the provided callback or the default one
        callback = callback_function if callback_function else default_callback

        try:
            # Start listening in the background
            stop_listening = r.listen_in_background(mic, callback)
            self.logger.info("Listening… say 'Hello EVA' to wake me up!")
            return stop_listening
        except Exception as e:
            error_msg = f"Failed to start background listening: {str(e)}"
            self.logger.error(error_msg)

    def run_speech_recognition(self):
        """
        Run the speech recognition in a loop until interrupted.
        The actual listening happens in a background thread created by listen_in_background.
        This loop just keeps the main program running and allows for graceful shutdown.
        """
        try:
            self.stop_listening = self.start_speech_recognition()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
            self.stop_listening()  # gracefully stop the background listener
        except Exception as e:
            self.logger.error(f"Fatal error in speech recognition: {str(e)}")

if __name__ == "__main__":
    try:
        stt = SpeechToText()
        stt.run_speech_recognition()
        while True:
            time.sleep(1)
            
    except Exception as e:
        logging.error(f"Application failed to start: {str(e)}")
        sys.exit(1)
