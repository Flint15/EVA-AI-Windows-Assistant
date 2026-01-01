import os
import config
from rapidfuzz import process
from typing import Union, Tuple
import threading
from threading import Thread
import functions 
import time
import logging
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track active search threads
active_search_threads = set()

def find_best_match(candidates: list[str], target_name: str) -> Union[str, None]:
	"""
	Find the best matching program name from a list of candidates using fuzzy matching.
	
	Args:
		candidates (list[str]): List of potential program names to search through
		target_name (str): The program name to find a match for
		
	Returns:
		Union[str, None]: The best matching program name if found (with score >= 91), None otherwise
	"""
	best_match: str = process.extractOne(target_name, candidates, score_cutoff=91)
	if best_match:
		return best_match[0]
	return None

def search_directory_recursive(root_path: str, target_program: str, should_delete: bool = False) -> Union[str, None]:
	"""
	Recursively search through all subdirectories for the target program.
	
	Args:
		root_path (str): The root directory to start searching from
		target_program (str): The name of the program to search for
		should_delete (bool): If True, delete the program when found
		
	Returns:
		Union[str, None]: The found program name if successful, None otherwise
	"""
	try:
		# Check if directory exists and is accessible
		if not os.path.exists(root_path) or not os.access(root_path, os.R_OK):
			logger.warning(f"Directory {root_path} is not accessible")
			return None

		while not config.stop_scaning.is_set():
			try:
				for current_dir, subdirs, files in os.walk(root_path):
					if config.stop_scaning.is_set():
						return None
						
					found_program = find_best_match(files, target_program)
					if found_program:
						logger.info(f'Program {config.programm_name} was found in {current_dir}')
						program_path = os.path.join(current_dir, found_program)
						
						try:
							if should_delete:
								functions.delete_object(program_path)
								config.stop_scaning.set()
								config.message_to_display = 'Object was found and deleted'
							else:
								# Store the found path and open the program
								config.application_paths['USER_CUSTOM_OBJECTS'][config.programm_name] = program_path
								functions.save_user_objects(program_path, config.programm_name)
								functions.open_object(program_path)
								config.stop_scaning.set()
								config.message_to_display = 'Object was found and opened'
						except Exception as e:
							logger.error(f"Error processing found program {found_program}: {e}")
							return None
				break
			except PermissionError:
				logger.warning(f"Permission denied accessing directory: {current_dir}")
				continue
			except Exception as e:
				logger.error(f"Error during directory walk: {e}")
				continue
	except Exception as e:
		logger.error(f"Error in search_directory_recursive: {e}")
	finally:
		# Remove this thread from active threads when done
		if threading.current_thread() in active_search_threads:
			active_search_threads.remove(threading.current_thread())

def separate_folders_and_files(directory: str) -> Tuple[Tuple[str], Tuple[str]]:
	"""
	Separate directory contents into folders and files, excluding unwanted items.
	
	Args:
		directory (str): The directory to analyze
		
	Returns:
		Tuple[Tuple[str], Tuple[str]]: A tuple containing two tuples:
			- First tuple: names of folders (excluding unwanted folders)
			- Second tuple: names of files (excluding unwanted files)
	"""
	try:
		if not os.path.exists(directory) or not os.access(directory, os.R_OK):
			logger.warning(f"Directory {directory} is not accessible")
			return ((), ())
			
		directory_contents = os.listdir(directory)
		
		# Filter folders, excluding unwanted ones
		folders = tuple(item for item in directory_contents 
					   if os.path.isdir(os.path.join(directory, item)) 
					   and item not in config.useless_content)
		
		# Filter files, excluding unwanted ones
		files = tuple(item for item in directory_contents
					 if os.path.isfile(os.path.join(directory, item)) 
					 and item not in config.useless_content)

		return (folders, files)
	except PermissionError:
		logger.warning(f"Permission denied accessing directory: {directory}")
		return ((), ())
	except Exception as e:
		logger.error(f"Error in separate_folders_and_files: {e}")
		return ((), ())

def search_directory(directory: str, folders: Tuple[str], files: Tuple[str], 
					target_program: str, should_delete: bool = False) -> Union[str, None]:
	"""
	Search for a program in the current directory and its subdirectories.
	
	Args:
		directory (str): The directory to search in
		folders (Tuple[str]): List of folders in the directory
		files (Tuple[str]): List of files in the directory
		target_program (str): The program to search for
		should_delete (bool): Whether to delete the program if found
		
	Returns:
		Union[str, None]: 'Object was found' if successful, None otherwise
	"""
	try:
		# First check files in current directory
		found_program = find_best_match(files, target_program)
		if found_program:
			program_path = os.path.join(directory, found_program)
			if not should_delete:
				config.application_paths['USER_CUSTOM_OBJECTS'][target_program] = program_path
				functions.save_user_objects(program_path, target_program)
				functions.open_object(program_path)
				config.stop_scaning.set()
				return 'Object was found and opened'
			else:
				functions.delete_object(program_path)
				config.stop_scaning.set()
				return 'Object was found and deleted'
		
		# If not found in current directory, search subdirectories
		for folder in folders:
			if not config.stop_scaning.is_set():
				folder_path = os.path.join(directory, folder)
				thread = Thread(target=search_directory_recursive, 
							  args=[folder_path, target_program, should_delete])
				thread.daemon = True
				active_search_threads.add(thread)
				thread.start()
			else:
				return None
	except Exception as e:
		logger.error(f"Error in search_directory: {e}")
		return None

def search_drive(drive_path: str, target_program: str, should_delete: bool = False) -> Union[str, None]:
	"""
	Search for a program in a specific drive.
	
	Args:
		drive_path (str): The drive to search in
		target_program (str): The program to search for
		should_delete (bool): Whether to delete the program if found
		
	Returns:
		Union[str, None]: 'Object was found' if successful, None otherwise
	"""
	try:
		if not os.path.exists(drive_path):
			logger.warning(f"Drive {drive_path} does not exist")
			return None
			
		if drive_path == 'C:\\':
			# For C drive, search only in specified paths
			for search_path in config.paths_for_searching:
				if config.stop_scaning.is_set():
					return None
				if not os.path.exists(search_path):
					logger.warning(f"Search path {search_path} does not exist")
					continue
					
				folders, files = separate_folders_and_files(search_path)
				if not folders and not files:  # Skip if directory is not accessible
					continue
					
				result = search_directory(search_path, folders, files, target_program, should_delete)
				if result and 'Object was found' in result:
					config.message_to_display = result 
		else:
			# For other drives, search the entire drive
			folders, files = separate_folders_and_files(drive_path)
			if not folders and not files:  # Skip if directory is not accessible
				return None
				
			result = search_directory(drive_path, folders, files, target_program, should_delete)
			if result and 'Object was found' in result:
				config.message_to_display = result 

	except Exception as e:
		logger.error(f"Error searching drive {drive_path}: {e}")
	finally:
		# Remove this thread from active threads when done
		if threading.current_thread() in active_search_threads:
			active_search_threads.remove(threading.current_thread())

def search_all_drives(drives: Tuple[str], target_program: str, should_delete: bool = False) -> None:
	"""
	Launch parallel searches across multiple drives.
	
	Args:
		drives (Tuple[str]): List of drives to search
		target_program (str): The program to search for
		should_delete (bool): Whether to delete the program if found
	"""
	for drive in drives:
		thread = Thread(target=search_drive, 
					   args=[drive, target_program, should_delete],
					   name=f'Search Thread {drive}')
		thread.daemon = True  # Make thread daemon so it exits when main program exits
		active_search_threads.add(thread)
		thread.start()

def scan_for_program(target_program: str, should_delete: bool = False) -> None:
	"""
	Main function to initiate the program search across all drives.
	
	Args:
		target_program (str): The name of the program to search for
		should_delete (bool): Whether to delete the program if found
	"""
	logger.info('Starting program scan')
	config.programm_name = target_program
	config.stop_scaning.clear()
	
	available_drives: Tuple[str] = functions.get_drives()
	search_all_drives(available_drives, target_program, should_delete)

if __name__ == '__main__':
	program_name = input('Enter the name of the program to search for: ')
	scan_for_program(program_name)
