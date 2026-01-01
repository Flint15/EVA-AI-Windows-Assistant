from PyQt5.QtCore import QMutex
import os
import threading

application_version: str = "1.1.0"

CWD = ''

# Valuable to manage which page to use (For message displaying)
current_page = None

# Translated words
translations_cache: dict = {}

# Common quiantity of all chats
chats_quantity: int = 0

# To track which chat page widget was clicked (to have ability to delete it later). 0 by default, because there is 0 chats initially.
current_page_widget_id: int = 0

# Current language
current_language_code: str = 'ru'
# Current language id
current_language_id: int = 3
# Available languages in ISO-639 format
available_languages: dict = {
    1: 'en',    # English
    2: 'ja',    # Japanese
    3: 'ru',    # Russian
    4: 'de',    # German
    5: 'es',    # Spanish
    6: 'fr',    # French
    7: 'it',    # Italian
    8: 'pt',    # Portuguese
    9: 'zh',    # Chinese
    10: 'ko',   # Korean
    11: 'ar',   # Arabic
    12: 'hi',   # Hindi
    13: 'nl',   # Dutch
    14: 'pl',   # Polish
    15: 'sv',   # Swedish
    16: 'no',   # Norwegian
    17: 'da',   # Danish
    18: 'fi'    # Finnish
}

# Create an Event to signal all threads to stop
stop_scaning = threading.Event()

call_words: list = ['eva', 'say']

#Flags:
voice_output_flag: bool = False # By default
grayscaling_flag: bool = False
# To check, does user want to voicing a message from Joy
voicing_message_flag: bool = False  
alarm_flag: bool = False

# Variable to check if llm was activated or not
# True, means llm was activated, False otherwise
llm_status: bool = False

# Variable to check if user should write directory ot not
# False meant not, True otherwise
music_directory_status: bool = False

app_directory_status: bool = False

# To check if tray feature is activated or not
tray_activation: bool = False

# To check if reminder is working or not
reminder_flag: bool = False

# For checking, is current time for alarm, or not
alarm_mutex = QMutex()
add_message_mutex = QMutex()

user_message: str = ''

MUSIC_JSON_FILE: str = 'user_custom_music.json'
MUSIC_SOURCE_DIRECTORY: str = ''
user_music: str = ''

programm_name: str = ''

# Contain time for alarm
user_alarm_time: str = ''

possible_message_from_llm: str = ''
message_to_display: str = ''

"""
We can change key and value like this:
    'open_features': ['open', 'show'],
    'play_feature': ['play', 'take on'],
    'say_features': ['say', 'show']
In this way user can call features with more commands capabilities
"""

# With data type on the end (e.g., .txt)
user_file_name: str = ''

new_image_path: str = ''

# Contains the path to an image
user_chat_files: dict = {}

# Contain exect directories to different Applications
application_paths: dict = {'USER_CUSTOM_OBJECTS': {}}

# Get the user's home directory directly
home_dir = os.path.expanduser('~')

# Only for C:
paths_for_searching: set = (f'{home_dir}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu',
                            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs',
                            r'C:\Program Files (x86)',
                            r'C:\Program Files'
                            )

useless_content: set = {'$GetCurrent','$SysReset','$WINDOWS.~BT','$Windows.~WS',
                        '$WinREAgent','adobeTemp','BIOS','DRIVER','Drivers','ESD',
                        'Intel','MSOCache','nltk_data','OneDriveTemp','PerfLogs',
                        'ProgramData','Python','QualityStats','SQLite','UserGuidePDF',
                        'Windows','Windows10Upgrade','$RECYCLE.BIN', '$Recycle.Bin',
                        'Boot','bootmgr','cmdlog.txt','Config.Msi','Documents and Settings',
                        'DumpStack.log','DumpStack.log.tmp','hiberfil.sys','IntelOptaneData',
                        'pagefile.sys','Recovery','swapfile.sys','System Volume Information',
                        'bdcamsetup.exe','ccsetup557.zip','ChromeSetup.exe','Downloads.rar',
                        'gtk-sharp-2.12.45.msi','HoydiXoIcons.zip','jre-8u341-windows-x64 (1).exe',
                        'jre-8u341-windows-x64.exe','MicrosoftEdgeSetup.exe','mono-6.8.0.105-x64-0.msi',
                        'NDP452-KB2901954-Web.exe','picasa39-setup - Ярлык.lnk'}

verbs_commands: dict = {
    'open': 'open_features',
    'play': 'play_feature',
    'say': 'say_features',
    'create': 'create_features',
    'search': 'search_features',
    'read': 'reading_feature'
}

instantaneous_tasks: dict = {
    'get_time': 'get_time',
    'get_date': 'get_date',
    'open_site': 'open_site',
    'control_volume': 'control_volume',
    'play_music': 'play_music',
    'search_information': 'search_information',
    'set_screen_brightness': 'set_screen_brightness',
    'calculate_expression': 'calculate_expression',
    'open_object': 'open_object',
    'activate_reminder_flag' : 'activate_reminder_flag'  # Also set_alarm, because its executes on the side
}

long_term_tasks: dict = {
    'scan_for_program': 'scan_for_program',
    'reorganize_by_extension': 'reorganize_by_extension',
    'create_reminder': 'create_reminder',
    'file_reading_thread': 'file_reading_thread',
    'start_sched': 'start_sched',
    'start_thread': 'start_thread'
}

task_descriptions: dict = {
    # Instantaneous Tasks
    'get_time': 'Returns the current system time in HH:MM:SS format',
    'get_date': 'Returns the current date in Day Month Year format',
    'open_site': 'Opens a website in the default browser',
    'control_volume': 'Controls system volume (increase/decrease/mute/unmute)',
    'play_music': 'Plays music files from the user\'s music collection',
    'search_information': 'Performs web searches using the default search engine',
    'set_screen_brightness': 'Adjusts the screen brightness level',
    'calculate_expression': 'Solves mathematical expressions',
    'open_object': 'Opens files or applications',
    'activate_reminder_flag': 'Sets up the creation of a new reminder',
    
    # Long-term Tasks
    'scan_for_program': 'Searches through the system for specific programs or files',
    'reorganize_by_extension': 'Reorganizes files in a directory by their file extensions',
    'create_reminder': 'Creates a new reminder with specified parameters',
    'set_alarm': 'Sets up an alarm for a specific time',
    'file_reading_thread': 'Reads file contents in a separate thread',
    'start_sched': 'Starts a scheduler for timed tasks',
    'start_thread': 'Manages thread creation and execution for background tasks',
    
    # Verb Commands
    'open': 'Opens files, applications, or websites',
    'play': 'Plays media files or music',
    'say': 'Provides voice output or reads text',
    'create': 'Creates new items like reminders or alarms',
    'search': 'Searches for information or files',
    'read': 'Reads file contents or text'
}

open_features: dict = {
    'open_site': {'youtube', 'google', 'soundcloud'}
}

play_feature: dict = {
    'play_music': None
}

say_features: dict = {
    'get_time': {'time'},
    'get_date': {'date'}
}

create_features: dict = {
    'set_alarm': {'alarm'},
    'activate_reminder_flag': {'reminder'}
}

search_features: dict = {
    'search_information': None
}

reading_feature: dict = {
    'read_file': 'file'
}
