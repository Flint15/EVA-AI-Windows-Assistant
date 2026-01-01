import json
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, Optional
import config

def load_exe_apps() -> Dict[str, str]:
    """Load the .exe apps from JSON file."""
    try:
        with open('all_apps_deduped.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: exe_apps.json not found. Please run the scanner first.")
        return {}

def clean_name_for_comparison(name: str) -> str:
    """Clean name for similarity comparison."""
    # Remove common words and special characters
    name = name.lower()
    name = name.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    name = name.replace('version', '').replace('v.', '').replace('v ', '')
    name = name.replace('64-bit', '').replace('32-bit', '').replace('x64', '').replace('x86', '')
    name = name.replace('professional', '').replace('pro', '').replace('plus', '')
    name = name.replace('edition', '').replace('enterprise', '').replace('home', '')
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    return name

def find_best_app_match(user_input: str, apps: Dict[str, str]) -> Optional[tuple[str, str, float]]:
    """
    Find the best matching app based on user input.
    Returns tuple of (app_name, app_path, similarity_score) or None.
    """
    if not apps:
        return None
    
    best_match = None
    best_score = 0
    clean_user_input = clean_name_for_comparison(user_input)
    
    for app_name, app_path in apps.items():
        clean_app_name = clean_name_for_comparison(app_name)
        
        # Calculate similarity score
        similarity = SequenceMatcher(None, clean_user_input, clean_app_name).ratio()
        
        # Additional scoring for common patterns
        if clean_app_name in clean_user_input or clean_user_input in clean_app_name:
            similarity += 0.2  # Bonus for substring matches
        
        # Exact match bonus
        if clean_user_input == clean_app_name:
            similarity += 0.5
        
        if similarity > best_score:
            best_score = similarity
            best_match = (app_name, app_path, similarity)
    
    return best_match

def launch_app(app_path: str, app_name: str = '') -> bool:
    """Launch the application using subprocess."""
    try:
        # Use subprocess.Popen to launch the application
        subprocess.Popen([app_path], shell=True)
        config.message_to_display = f'{app_name} was opened'
        
    except Exception as e:
        print(f"Error launching application: {e}")
        return False

def open_application(app_name: str) -> bool:
    """
    Main function to open an application by name.
    Returns True if successful, False otherwise.
    """
    # Load available apps
    apps = load_exe_apps()
    if not apps:
        return False
    
    # Find best match
    match = find_best_app_match(app_name, apps)
    
    if match:
        app_name_found, app_path, similarity = match
        
        # Launch the app (no confirmation needed for external calls)
        return launch_app(app_path, app_name=app_name_found)
    else:
        return False
