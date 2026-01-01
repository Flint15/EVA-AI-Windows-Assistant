import sys
import logging
from typing import Union
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from message_processor import MessageProcessor
from UI_Threads import LLMStreamingThread
from UI import MainWindow
import config, functions
import load_user_data
import llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
EVA_main.py

Main entry point for the EVA application. This script initializes the main window, sets up the message processor, 
LLM, and handles user input (both text and voice) using PyQt5.
"""

class MainApp(MainWindow):
    """
    Main application window class for EVA.
    Inherits from MainWindow and sets up message processing, LLM, and voice input handling.
    
    Attributes:
        processor (MessageProcessor): Handles processing of user commands
        llm (LLM): Language model instance for generating responses
        voice_input_thread (VoiceRequiestHandler): Thread for handling voice input
        current_llm_thread (LLMStreamingThread): Current active LLM streaming thread
    """
    
    def __init__(self):
        """Initialize the main application window and its components."""
        super().__init__()
        
        # Set up working directory
        working_dir = Path(__file__).resolve().parent
        config.CWD = working_dir
        logger.info(f'Current working directory - {config.CWD}')
        
        # Initialize core components
        self.processor = MessageProcessor(config, functions)
        self.llm = llm.LLM()
        
        # Set up message handling
        self.message_signal.connect(self._handle_command)
        
        # Initialize user data
        functions.create_objects_json()
        load_user_data.load_user_settings()
        
        # Initialize LLM streaming
        self.current_llm_thread = None
        
    def _process_message(self, user_command: str, page_id) -> Union[None, str]:
        """
        Process a user command and determine the appropriate response or action.
        Handles threading for image processing and LLM responses.
        
        Args:
            user_command (str): The command entered by the user
            page_id: The current page identifier
            
        Returns:
            Union[None, str]: The response to display or None
        """
        try:
            # Show typing indicator while processing
            self.display_response(placeholder=True, page_id=page_id)
            
            # Process the command
            response = self.processor.process_user_input(user_command)
            try:

                processed_result: str = response[0]
                user_message_type: str = response[1]

                self._create_response(page_id, processed_result, user_message_type)
    
            except Exception as e:
                logger.error(f'Error processing command response: {str(e)}')
                
        except Exception as e:
            logger.error(f'Error in message processing: {str(e)}')

    def _create_response(self, page_id, processed_result: str, user_message_type: str) -> None:
        try:
            print(page_id)
            print(self.existed_pages)
            print(config.current_page)
            self.current_llm_thread = LLMStreamingThread(
                chat_page=config.current_page,
                processed_result=processed_result,
                user_message_type=user_message_type
            )
        except Exception as e:
            self.logger.error(f'Error in `_create_response`, while trying to initialize LLMStreamingThread, error - {e}')
            return
        self.current_llm_thread.start()

    def _handle_command(self, command_info: tuple) -> Union[None, str]:
        """
        Handle commands entered in the input box.
        
        Args:
            command_info (tuple): Tuple containing user command and page id
            
        Returns:
            Union[None, str]: The response to display or None
        """
        user_command: str = command_info[0]
        page_id = command_info[1]
        
        # Update current state
        config.user_message = user_command

        return self._process_message(user_command, page_id)

if __name__ == "__main__":
    """Main entry point for the EVA application."""
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
