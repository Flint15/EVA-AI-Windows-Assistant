import os
import json
import logging
from src.core import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_user_data(data) -> None:
	try:
		if os.path.exists('user_custom_apps.json'):
			app_name, app_path = data[0], data[1]

			with open('user_custom_apps.json', 'r') as file:
				data = json.load(file)
			data['USER_APPS'][app_name] = app_path
			with open('user_custom_apps.json', 'w') as file:
				json.dump(data, file, indent=2)
				logger.info('Information about custom Application was saved')
	except Exception as e:
		print(f'Error in `load_user_data` in `save_user_data`')

def load_custom_objects() -> None:
	"""
	Update config.open_features
	"""
	try:
		if os.path.exists('user_custom_objects.json'):
			with open('user_custom_objects.json', 'r') as file:
				data = json.load(file)
				config.application_paths = data
				logger.info('Custom user apps was loaded in config')
		return None

	except Exception as e:
		logger.error(f'Error in `load_user_data.py`, in "load_custom_apps" - {e}')

def load_user_language_settings(languages) -> None:
	"""
	Load language settings from user_settings.json.
	Updates config.current_language_conf and config.current_language_id.
	Falls back to English if settings are invalid or missing.
	"""
	try:
		if os.path.exists('user_settings.json'):
			with open('user_settings.json', 'r') as file:
				data: dict = json.load(file)
				config.current_language_code = data['LANGUAGE']
				config.current_language_id = languages.get_id_by_code(config.current_language_code)
				logger.info('Language was seted')
	except Exception as e:
		logger.error(f'Error in `load_user_language_settings`, error - {e}')

def load_user_settings():
	load_custom_objects()

def load_music_data(directory: str) -> list:
	"""
	Get exect names of musics name in the given directory.
	
	Returns: List of .mp3 files
	"""

	# List all entries (files and directories) in the current directory
	entries = os.listdir(directory)

	# Filter out only files by checking each entry
	files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry)) and entry.lower().endswith('.mp3')]

	return files

def load_app_data(directory: str) -> list:
	"""
	Get exect names of rpgramms name in the given directory.
	
	Returns: List of .exe files
	"""
	logger.info(f'Directory - {directory}')
	entries = os.listdir(directory)
	files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry)) and entry.lower().endswith('.exe')]
	logger.info(f'files - {files}')
	return files

def load_user_voice_status() -> bool:
	"""
	On the current time, just load voicing_output_status in config
	"""

	if os.path.exists('user_settings.json'):
		try:
			with open('user_settings.json', 'r') as file:
				data = json.load(file)
				voice_output_status: bool = bool(data['VOICING_OUTPUT_STATUS'])
				logger.info(f'User settings: current(last) voicing_output_status - {voice_output_status}')
				config.voicing_message_flag: bool == voice_output_status
				return voice_output_status
		except Exception as e:
			logger.error(f'Error in `load_user_settings`, error - {e}')
			return True
	else:
		return False

if __name__ == '__main__':
	files = load_app_data(r'C:\Users\chess\AppData\Local\Programs\obsidian')

	print(files)
