import time 
import datetime
import webbrowser
import psutil
from src.core import config
import os
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # For control_volume
from comtypes import CLSCTX_ALL     
import json
from typing import Union, List, Dict, Optional
from src.data import load_user_data
from rapidfuzz import process
import re
import logging
import threading
import sched
from src.audio import tts
import locale
import screen_brightness_control as sbc
from src.features import math_func

scheduling = sched.scheduler()
calc = math_func.Calculator()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_time(arg = None) -> str:
    """
    Return the current system time in HH:MM:SS format.
    
    Args: 
        arg: Unused parameter (maintained dor interface consistnecy)
    Returns:
        str: Current time formatted as '%H:%M%S'
    """

    return time.strftime('%H:%M:%S')

def get_date(arg = None) -> str:
    """
    Return the current date in 'Day Month Year' format.
    
    Args: 
        arg: Unused parameter (maintained dor interface consistnecy)
    Returns:
        str: Current date formatted as '13 February 2025'
    """

    now = datetime.datetime.now()   

    return f'{now.day} {now.strftime("%B")} {now.year}'

def open_site(website) -> Optional[str]:
    """
    Open a website in default browser after URL formatting.

    Process input to create valid URL:
    - Replace 'dot com' with .com
    - Appends '.com' if missing

    Args:
        website (str): Website name (e.g. 'google' or 'spasex dot com')
    Returns:
        str: Success message if successful, None on error
    Raises:
        Exception: Captures and prints browser-realated errors.
    """

    # Process the input to create a valid URL
    try:
        if 'dot com' in website:
            website = website.replace('dot com', '.com')
        else:
            website += '.com'

        url = f'https://www.{website}'
            
        try:    
            webbrowser.open(url)
            time.sleep(2) # Wait for the browser to open
        except Exception as e:
            logger.error(f'Error opening site: {e}')

            return None

        return 'Website was opened successfully'           
    except Exception as e:
        logger.error(f'Error while trying to open website, error - {e}')          

def control_volume(action: str) -> str:
    """
    Control the system volume using pycaw library.

    Supported actions:
    - increase: Boost volume by 10%
    - decrease: Reduce volume by 10%
    - mute: Silence output
    - unmute: Restore sound

    Args:
        action (str): Volume control command
    Returns:
        str: Operation result message
    Raises:
        WindowsError: If audio interface is unavailable
    
    """

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

    if action == 'increase':
        # Increase volume on specific level (10% of max level)
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
        return 'Volume has been increased successfully'

    if action == 'decrease':
        # Decrease volume on specific level (10% of max level)
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
        return 'Volume has been decreased successfully'

    if action == 'mute':
        # Mute the volume
        volume.SetMute(1, None)
        return 'Volume has been muted successfully'
          
    if action == 'unmute':
        # Unmute the volume
        volume.SetMute(0, None)
        return 'Volume has been unmuted successfully'

def clear_user_apps() -> None:
    """
    Reset user applications configuration.

    Note:
        Writes empty dictionary to JSON storage
    """

    config.user_apps_path = {} # Reset the dictionary
    with open('user_apps.json', 'w') as file:
        json.dump({}, file, indent=4) # Save an empty dictionary

def load_music_data() -> Union[Dict, str]:
    """
    Load music database from JSON file.

    Returns:
        Union[Dict, str]: Music data or error message

    Note:
        Creates enpty database if file is corrupted
    """
    try:
        with open(config.MUSIC_JSON_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return'Warning: JSON file is corrupted. Starting with an empty music database'

def save_music_data(data: Dict, user_music: str, path: str) -> None:
    """
    Update music database with new entry.

    Args:
        data (Dict): Existing music data
        user_music (str): Track name identifier
        path (str): Full filesystem path to music file
    """
    data['USER_MUSICS'][user_music] = path
    with open(config.MUSIC_JSON_FILE, 'w') as file:
        json.dump(data, file, indent=3)

def check_and_create_directory(directory: str) -> Union[Dict, None]:
    """
    Validate music directory and load database.

    Args:
        directory (str): Path to music storage location

    Returns:
        Optional[Dict]: Music data if directory exists else None
    """

    if not os.path.isdir(directory):
        logger.error('Error: The provided directory does not exist.')
        return None
    
    if config.MUSIC_SOURCE_DIRECTORY == '':
        config.MUSIC_SOURCE_DIRECTORY = directory

    with open(config.MUSIC_JSON_FILE, 'r') as file:
        return json.load(file)

def add_music_entry(directory: str) -> str:
    """
    Register new music file in database.
    
    Args:
        directory (str): Path containing music files

    Returns:
        str: Operation status message

    Note:
        Uses fuzzy matching for track name resolution
    """

    try:
        data = check_and_create_directory(directory)
        list_music_name = load_user_data.load_music_data(directory)
        true_music_name = process.extractOne(config.user_music, list_music_name)

        # Construct the full path to the .mp3 file
        file_path = os.path.join(directory, f'{true_music_name[0]}')
        # Optianally warn if the file doesn't exist at the given location
        if not os.path.exists(file_path):
            logger.error('Warning: The music file does not exist at the specified path!')

        save_music_data(data, config.user_music, file_path)
        launch_music(file_path)

        return 'Music was loaded and playing successfully'
    except Exception as e:
        return f'Error in add_music_entry - "{e}"'

def launch_music(music: str) -> None:
    """
    Start music playback using default player.

    Args:
        music (str): Path to music file
    """

    os.startfile(music)

def play_music(music_name: str) -> str:
    """
    Main music playback controller.

    Args:
        music_name (str): Track name to play

    Returns:
        str: Playback status message

    Note:
        Guides user through setup if database missing
    """
    """
    Search music by using PC scaning
    """
    try:
        if os.path.exists(config.MUSIC_JSON_FILE):
            # If 'user_custom_music.json' exists
            data = load_user_data.load_music_data()
        else:
            # If 'user_custom_music.json' doesn't exists
            with open(config.MUSIC_JSON_FILE, 'a') as file:
                json.dump({'USER_MUSICS': {}}, file)
            config.user_music = music_name
            config.music_directory_status = True
            return 'Please provide the directory where your music is saved - '

        if music_name in data.get('USER_MUSICS', {}):
            file_path = data['USER_MUSICS'][music_name]         
            try:
                os.startfile(file_path)
                return 'Music was playing successfully'
            except Exception as e:
                logger.error(f'Failed to open the music file: {e}')
        else:
            config.user_music = music_name
            return add_music_entry(config.MUSIC_SOURCE_DIRECTORY)
    except Exception as e:
        logger.error(f'Error in play_music - "{e}"')

def trigger_alarm() -> str:
    """
    Execute alarm
    """
    return f'It\'s an alarm on {config.user_alarm_time}'

def check_digits(user_command: str) -> str:
    """
    This function extract time (numbers, devided by `:` ) from user command
    Also, save this time in `config.py` 

    Args:
        user_command (str): Contain user message

    Returns:
        str: Exect time, for example 17:34  
    """
    try:
        if any(i.isdigit() for i in user_command):
            alarm_time = re.search(r'\d{1,2}:\d{2}', user_command).group()
            config.user_alarm_time = alarm_time

            return alarm_time
    except Exception as e:
        logger.error(f'Error in "check_digits", with error - {e}')

def get_hour_min(current_time: str = get_time()) -> str:
    """
    Change `%H:%M:%S` format in `%H:%M`

    Args:
        current_time (str): Current time in `%H:%M:%S` format
                            object from `get_time` function, by default

    Returns:
        str: time in `%H:%M`
    """

    try:
        # Split the `current_time` at each colon
        parts = current_time.split(':')
        # Extract hours and minutes (first 2 parts) and join them with a colon
        hours_minutes = f'{parts[0]}:{parts[1]}'
        return hours_minutes
    except Exception as e:
        logger.error(f'Error in "get_hour_min", with error - {e}')

def turn_alarm_flag() -> None:
    config.alarm_flag = True

def start_sched(time: int) -> None:
    try:
        scheduling.enter(time, 1, turn_alarm_flag)
        scheduling.run()
    except Exception as e:
        logger.error(f'Error in "start_sched", with error - {e}')

def start_thread(time: int) -> None:
    try:
        thread = threading.Thread(target=start_sched, args=(time,))
        thread.start()
    except Exception as e:
        logger.error(f'Error in "start_thread", with error - {e}')

    return 'Alarm on {config.user_alarm_time} is seted'

def define_time_difference(current_time: str, alarm_time: str) -> int:
    """
    This function get difference between current and alarm time, in secunds, through a several steps:
        
        1. Split each time type (current, alarm) at each colon
        2. Create a new lists, that contain each parts as integer
        3. Get common minutes value, of each time type
        4. Define secunds difference between current and alarm time
    
    Args: 
        current_time (str): Current time in `%H:%M` format
        alarm_time (str): Alarm time in `%H:%M` format

    Returns:
        int: 

    """

    try:
        current_time_parts: list = current_time.split(':')
        alarm_time_parts: list = alarm_time.split(':')

        current_time_parts: List[int] = [int(i) for i in current_time_parts]
        alarm_time_parts: List[int] = [int(i) for i in alarm_time_parts]

        current_minutes_time: int = current_time_parts[0] * 60 + current_time_parts[1]
        alarm_minutes_time: int = alarm_time_parts[0] * 60 + alarm_time_parts[1]

        time_difference_in_secunds = abs(current_minutes_time - alarm_minutes_time) * 60

        # Debugging
        logger.info(f'Current time - {current_time_parts}, Alarm time - {alarm_time_parts}')
        logger.info(f'Current time in minutes - {current_minutes_time}, alarm time in minures - {alarm_minutes_time}')
        logger.info(f'Secunds difference - {time_difference_in_secunds}')

        return start_thread(time_difference_in_secunds)

    except Exception as e:
        logger.error(f'Error in "define_time_difference", with error - {e}')

def set_alarm(user_command: str) -> None:
    """
    Set the alarm.
    First, get time from user message, and then current time. All in the same format.

    Args:
        user_commmand (str): User message

    Returns:
        str: 
    """
    try:
        alarm_time: str = config.user_alarm_time
        current_time: str = get_hour_min()
        
        # For debugging
        logger.info(f"""    User wanted time for alarm - {alarm_time}
                Current time - {current_time}
        """)

        return define_time_difference(current_time, alarm_time)
    except Exception as e:
        logger.error(f'Error in "set_alarm", with error - {e}')

def check_voicing_flag(text):
    if config.voicing_message_flag:
        tts.voice_output(text)
    return None 

def is_browser_installed(path: str) -> bool:
    """
    Checks whether the browser is installed on the specified path.

    :param
        path(str): the path to the application
    :return:
        bool: Does the path exist or not (True/False)
    """
    try:
        logger.info(f"path of current browser is - {os.path.exists(path)}")
        return os.path.exists(path)
    except Exception as e:
        logger.error(f'Error in "is_browser_installed", with error - {e}')
def is_browser_running(name: str) -> bool:
    """
    Checking for a running browser.

    :param
        name(str): name of browser
    :return:
        bool: Is the browser running or not (True/False)
    """

    try:
        for process in psutil.process_iter(['name']):
            if process.info['name'] and name in process.info['name'].lower():
                logger.info(f"{name} - were founded")
                return True
        return False
    except Exception as e:
        logger.error(f'Error in "is_browser_running", with error - {e}')

def get_user_language() -> str:
    """
    Defines the language of the user's system.

    :return:
        str: the user's system language in the form of two characters (for example - 'ru')
    """

    try:
        language = locale.getlocale()[0] or "en_US"
        logger.info(f"User's language is - {language.lower()}")
        return language.lower()
    except Exception as e:
        logger.error(f'Error in "get_user_language", with error - {e}')

def search_information(user_command: str) -> str:
    """
    The main process of launching the browser and searching for information

    :param
        query(str): user's request

    """
    try:
        language = get_user_language()
        if language.startswith("ru"):
            url = f"https://www.yandex.ru/search/?text={user_command.replace('search ', '', 1)}"
        else:
            url = f"https://www.google.com/search?q={user_command.replace('search ', '', 1)}"

        webbrowser.open(url)

        logger.info(f"Process in search_information was succeccful, user's command - {user_command.replace('search ', '', 1)}")
        return f"Here is your request about '{user_command.replace('search ', '', 1)}'"
    except Exception as e:
        logger.error(f'Error in "search_information", with error - {e}')

def save_user_settings(status: bool) -> str:
    """
    Save voicing status into 'user_settings.json'
    """
    with open('user_settings.json', 'r') as file:
        data: dict = json.load(file)
    with open('user_settings.json', 'w') as file:
        data['VOICING_OUTPUT_STATUS'] = f'{status}'
        json.dump(data, file)

def get_drives() -> tuple[str]:
    try:
        """
        Get available drives from System
        """
        partitions = psutil.disk_partitions(all=False)
        drives = [partition.mountpoint for partition in partitions if partition.fstype != '']
        logger.info(f'Finded drives - {", ".join(drives)}')
        return drives
    except Exception as e:
        logger.info(f'Error in "get_drives" with error - "{e}"')

def start_file_processing(file_path: str, file_name: str) -> str:
    """
    Processe file
    """
    config.user_chat_files[file_name] = file_path
    config.user_file_name = file_name

    return f'{file_name} was saved'

def file_reading_thread(text: str) -> str:
    """
    This function call the function that processed file selected by the user, in the another Thread
    
    Args:
        file_path (str): Contain exect directory to file
        file_name (str): Name of the file, with data type on the end (e.g., '.exe')
    
    Returns:
        ?
    """
    try:
        none_object = None
        thread = threading.Thread(target=tts.play_audio, args=(text, none_object),daemon=True)
        thread.start()
    except Exception as e:
        logger.error(f'Error in file_processor_thread, error - {e}')

    return 'File was readed successfully!'

def read_file(file_path: str = None, file_name: str = None) -> str:
    try:
        file_name = config.user_file_name
        file_path = config.user_chat_files[file_name]

        if os.path.exists(file_path):
            with open(file_name, 'r') as file:
                content = file.read()
                file_reading_thread(content)
                return 'Reading the content...'
        else:
            return f'This file doesn\'t exists'
    except Exception as e:
        logger.error(f'Error in read_file, error - {e}')
def set_screen_brightness(user_input: str) -> None:
    """
    Adjusts screen brightness based on user input.
    Supports increasing/decreasing brightness by specified value or setting default (20%).

    :param user_input:
        str: User command containing brightness value and operation
             (e.g. "increase 15", "decrease 10")
    :return:
        None
    """

    try:
        # Extract numeric value from input or use default (20)
        match = re.search(r'-?\d+\.?\d*', user_input)
        new_value = float(match.group()) if match else 20

        current_brightness = sbc.get_brightness()

        # Process brightness adjustment
        if 'increase' in user_input.lower():
            if current_brightness[0] + new_value <= 100:
                sbc.set_brightness(current_brightness[0] + new_value)
            else:
                sbc.set_brightness(100)
        elif 'decrease' in user_input.lower():
            if current_brightness[0] - new_value >= 0:
                sbc.set_brightness(current_brightness[0] - new_value)
            else:
                sbc.set_brightness(0)

        logger.info(f"Brightness changed. Current: {current_brightness}%")
        return f"Current brightness: {sbc.get_brightness()[0]}%"

    except Exception as e:
        logger.error(f'Error in "set_screen_brightness": {e}')
        
def calculate_expression(user_input: str) -> None:
    try:
        user_request = user_input.replace('solve ', '')
        result = calc.safe_eval(user_request)
        return f"Result: {result}"
    except Exception as e:
        logger.error(f'Error in "calculate_expression", with error - {e}')

def open_object(path_to_object: str):
    try:
        os.startfile(path_to_object)
        logger.info(f'Object {config.programm_name} was opened')
        config.message_to_display = f'{config.programm_name} was opened'
    except Exception as e:
        logger.error(f'Error in "open_object", error - {e}')

def create_objects_json():
    if not os.path.exists('user_custom_objects.json'):
        with open('user_custom_objects.json', 'a') as file:
            json.dump({'USER_CUSTOM_OBJECTS': {}}, file, indent=2)

def create_user_settings_language():
    pass

def save_user_objects(path_to_object: str, object_name: str):
    with open('user_custom_objects.json', 'r') as file:
        data: dict = json.load(file)
        #{'USER_CUSTOM_OBJECTS': {}}
    data['USER_CUSTOM_OBJECTS'][object_name] = path_to_object
    #{'USER_CUSTOM_OBJECTS': {'discord.exe': 'C:\'}}
    with open('user_custom_objects.json', 'w') as file:
        json.dump(data, file, indent=3)

def activate_reminder_flag(none_object = None) -> str:
    # Activate reminder flag
    config.reminder_flag = True
    return '''Enter the data for your note in the format:
        Name your reminder | Message your reminder | Time your reminder(Format: DD.MM.YYYY HH:MM) | Duration your reminder | Location your reminder | Reminder minute before start
        '''

def delete_object(path_to_object: str):
    if os.path.exists(path_to_object):
        try:
            os.remove(path_to_object)
            logger.info(f'Programm under {path_to_object} was deleted')
        except PermissionError:
            logger.error(f'Permission denied: cannot delete the file under {path_to_object}')
    else:
        logger.info(f'File under {path_to_object} doesn\'t exist')

if __name__ == '__main__':
    print(get_time())
