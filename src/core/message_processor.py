from dataclasses import dataclass
from src.core import config
from src.features import functions
from typing import Union, Tuple
import string
import logging
from src.core import llm
from src.core import verb_object_extractor
import re
from rapidfuzz import process, fuzz
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CommandResult:
    """
    Data structure to store the result of command processing.
    
    Attributes:
        success (bool): Indicates whether the command was executed successfully
        message (str): Response message or error description
    """
    success: bool
    message: str

class MessageProcessor:
    """
    Main class for processing natural language commands and mapping them to
    predefined system functions through configuration mappings.
    
    This class handles the entire pipeline of:
    1. Preprocessing user input
    2. Extracting commands and arguments
    3. Mapping to system functions
    4. Executing appropriate actions
    """
    
    def __init__(self, config: object, functions: object):
        """
        Initialize the MessageProcessor with configuration and function mappings.

        Args:
            config: Module containing command configuration mappings
            functions: Module containing executable functions for commands
        """
        self.config = config
        self.functions = functions
        self.extractor = verb_object_extractor.Extractor()   # NLP verb-object extractor
        self.llm = llm.LLM()               # Language Model instance
        logger.info('Message Processor initialized')

    def _process_message(self, action_verb: str, target_object: str) -> CommandResult:
        """
        Execute the processing pipeline for a recognized command.
        
        Args:
            action_verb: Action verb extracted from user input
            target_object: Target object/argument for the verb

        Returns:
            CommandResult: Contains execution status and message
        """
        system_command = self.define_command(action_verb)

        if system_command == 'Command wasn\'t defined':
            return 'Command wasn\'t defined'
            
        feature = self.define_feature(system_command, target_object)
        
        logger.info(f'Result of `process_command` - {feature}')

        if not feature == 'Feature wasn\'t finded!' and not feature[0] == 'open_file':
            try:
                function_name, argument = feature[0], feature[1]
                # Execute corresponding function from functions module
                logger.info(f'Executing function: {function_name} with argument: {argument}')
                result = getattr(self.functions, function_name)(argument)
                logger.info(f'Function execution result: {result}')
                return result
            except Exception as e:
                logger.info(f'Error in process_command: {str(e)}')
                return f'Error in process_command: {str(e)} \n'
        elif feature[0] == 'open_file':
            return functions.open_file(feature[1])
        
        return 'Feature wasn\'t finded!'    

    def define_command(self, action_verb: str) -> str:
        """
        Map natural language verb to system command using config.

        Args:
            action_verb: Action verb extracted from user input

        Returns:
            str: Corresponding system command name or error message
        """
        try:
            system_command = self.config.verbs_commands[action_verb]
            logger.info(f'Mapped to system command: {system_command}')
            return system_command
        except KeyError:
            logger.info(f'Command mapping not found for verb: {action_verb}')
            return 'Command wasn\'t defined'

    def define_feature(self, system_command: str, target_object: str) -> Union[tuple, str]:
        """
        Find executable feature and argument for a given system command.

        Args:
            system_command: System command name from define_command(), name from `verbs_command`
            target_object: Argument extracted from user input

        Returns:
            Tuple[str, str]: (feature_name, argument) if match found
            str: Error message if no match
        """
        best_match_score = 0
        best_feature = None
        best_argument = None

        try:
            for feature, constraints in getattr(self.config, system_command).items():
                if constraints is not None:
                    # Feature with predefined argument constraints
                    try:
                        match_result = process.extractOne(target_object, constraints)
                        if match_result[1] > 70 and match_result[1] > best_match_score:
                            best_match_score = match_result[1]
                            best_feature = feature
                            best_argument = target_object
                    except:
                        continue
                else:
                    # Feature without argument constrains (e.g. play_music)
                    return feature, target_object 
        except Exception as e:
            logger.error(f'Error in `define_feature`, error - {e}')

        if best_feature:
            return best_feature, best_argument
        return self._handle_feature_not_found(system_command, target_object)

    def _handle_feature_not_found(self, system_command: str, target_object: str) -> Union[Tuple[str, str], str]:
        """
        Handle cases when no feature mapping is found.

        Args:
            system_command: System command name
            target_object: Target object/argument

        Returns:
            Union[Tuple[str, str], str]: Feature mapping or error message
        """
        if system_command == 'open_features':
            return ('open_file', target_object)
        return 'Feature wasn\'t found'

    def _preprocess_input(self, user_input: str) -> str:
        """
        Clean and normalize user input for processing.

        Args:
            user_input: Raw input string from user

        Returns:
            str: Normalized text ready for NLP processing
        """
        logger.info(f'Original user input: "{user_input}"')

        try:
            # Check for time-related input
            functions.check_digits(user_input)

            # Basic text normalization
            normalized_text = user_input.strip().lower()
            # Remove punctuation
            normalized_text = normalized_text.translate(str.maketrans('', '', string.punctuation))
            # Normalize whitespace
            cleaned_text = re.sub(r'\s+', ' ', normalized_text)

            logger.info(f'Preprocessed input: "{cleaned_text}"')
            return cleaned_text
        except Exception as e:
            logger.error(f'Error in input preprocessing: {e}')

    def _handle_open_command(self, user_input: str) -> str:
        """
        Handle commands related to opening files or applications.

        Args:
            user_input: User command containing 'open' keyword

        Returns:
            str: Result of the open operation
        """
        try:
            target_object: str = ' '.join(word for word in user_input.split() if word != 'open')
            
            # Check for non-PC file opening
            for feature, valid_targets in config.open_features.items():
                if target_object in valid_targets:
                    logger.info('Processing non-PC file open request')
                    return getattr(self.functions, feature)(target_object), 'Instantanious Task'
            
            # Check for custom application paths
            logger.info('Processing PC file open request')
            for app_name, app_path in config.application_paths['USER_CUSTOM_OBJECTS'].items():
                if app_name == target_object:
                    functions.open_object(app_path)
            
            return ('opening', target_object), 'Long-Term Task'
        except Exception as e:
            logger.error(f'Error in open command handling: {e}')

    def _handle_special_cases(self, user_message: str) -> Union[str, Tuple[str, str]]:
        """
        Handle special command cases that require specific processing.

        Args:
            user_message: Raw user input message

        Returns:
            str: Processing result or 'Not exception case' if no special case matched
        """
        try:
            # Handle music directory input
            if config.music_directory_status:
                config.music_directory_status = False
                return functions.add_music_entry(user_message)

            # Handle reminder creation
            if config.reminder_flag:
                thread = Thread(target=create_reminder, args=[user_message])
                thread.start()
                return 'Reminder created successfully', 'Instantanious Task'

            # Handle file reorganization
            if 'reorganize' in user_message:
                target_path = ' '.join(word for word in user_message.split() if word != 'reorganize')
                thread = Thread(target=reorganize_by_extension, args=[target_path])
                thread.start()
                return ('reorganization', target_path), 'Long-Term Task'

            # Handle file opening
            if 'open' in user_message:
                return self._handle_open_command(user_message)

            # Handle file deletion
            if 'delete' in user_message:
                target_object = ' '.join(word for word in user_message.split() if word != 'delete')
                return ('deletion', target_object), 'Long-Term Task'

            # Handle search
            if 'search' in user_message:
                return functions.search_information(user_message)

            # Handle calculations
            if 'solve' in user_message:
                return functions.calculate_expression(user_message), 'Instantanious Task'

            # Handle brightness control
            if 'brightness' in user_message:
                return functions.set_screen_brightness(user_message), 'Instantanious Task'

            # Handle volume control
            if 'volume' in user_message:
                action_verb, _ = self.extractor.extract_verb_object(user_message)
                return functions.control_volume(action_verb), 'Instantanious Task'

            # Handle grayscale conversion
            if 'gray' in user_message:
                return ('image processing', config.user_chat_files[config.user_file_name]), 'Long-Term Task'

            return 'Not exception case'
            
        except Exception as e:
            logger.error(f'Error in special case handling: {e}')

    def process_user_input(self, user_input: str) -> Union[str, Tuple[str, bool, str]]:
        """
        Main entry point for processing user input.

        Args:
            user_input: Raw input string from user

        Returns:
            Union[str, Tuple[str, bool, str]]: Processing result or LLM streaming tuple
        """
        try:
            # Handle special cases first
            result = self._handle_special_cases(user_input)
            if result == 'Not exception case':
                # Process as regular command
                preprocessed_input = self._preprocess_input(user_input)
                action_verb, target_object = self.extractor.extract_verb_object(preprocessed_input)
                result = self._process_message(action_verb, target_object), 'Instantanious Task'
                if result[0] == 'Feature wasn\'t finded!' or result[0] == 'Command wasn\'t defined':
                    return user_input, 'Chatting'
            return result

        except Exception as e:
            logger.error(f'Error processing input: {str(e)}')
            return f'Error processing input: {str(e)} \n'

if __name__ == '__main__':
    processor = MessageProcessor(config, functions)
    user_input = input('Enter your command: ')
    response = processor.process_user_input(user_input)
    print(response)
