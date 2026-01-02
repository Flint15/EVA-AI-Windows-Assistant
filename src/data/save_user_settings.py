import json
import os
import logging

logger = logging.getLogger(__name__)

def read_settings_file(file_name: str = 'user_settings.json') -> dict:
	if os.path.exists('user_settings.json'):
		try:
			with open('user_settings.json', 'r') as file:
				data: dict = json.load(file)
		except json.JSONDecodeError:
				data = {}
		return data
	else:
		data = {}
		return data

def save_settings_file(data: dict, file_name: str = 'user_settings.json') -> None:
	"""
	Save settings to a file.
	"""
	try:
		with open(file_name, 'w') as file:
			json.dump(data, file, indent=2)
	except Exception as e:
		logger.error(f"Error saving settings file: {e}")
		raise


def save_language_settings(language: str) -> None:
	"""
	Save language settings to user_settings.json.
	
	Args:
		language: The language to save (must be a valid language from config)
	
	Raises:
		ValueError: If the language is invalid
	"""
	try:	
		# Read existing settings or create new dict
		data = read_settings_file()
		# Update language setting
		data['LANGUAGE'] = language
		
		# Save to file
		with open('user_settings.json', 'w') as file:
			json.dump(data, file, indent=2)
			
		logger.info(f"Language settings saved: {language}")
		
	except Exception as e:
		logger.error(f"Error saving language settings: {e}")
		raise

