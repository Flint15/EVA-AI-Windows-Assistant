from pathlib import Path
from difflib import SequenceMatcher
import json

def find_exe_files(apps: dict) -> dict:
    """
    Extract .exe files from the apps dictionary and find their exact paths.
    Save a dict with original names and exact .exe paths.
    """
    exe_apps = {}
    
    for name, path in apps.items():
        path_obj = Path(path)
        
        # If path is already a .exe file
        if path_obj.suffix.lower() == '.exe' and path_obj.exists():
            exe_apps[name] = str(path_obj)
            continue
            
        # If path is a directory, search for .exe files
        if path_obj.is_dir():
            # Look for .exe files in the directory
            exe_files = list(path_obj.glob('*.exe'))
            
            if exe_files:
                # If multiple .exe files found, use similarity to find the best match
                if len(exe_files) > 1:
                    best_match = find_best_exe_match(name, exe_files)
                    if best_match:
                        exe_apps[name] = str(best_match)
                else:
                    # Single .exe file found
                    exe_apps[name] = str(exe_files[0])
    
    save_exe_apps_to_config(exe_apps)

def find_best_exe_match(app_name: str, exe_files: list) -> Path:
    """
    Find the best matching .exe file based on name similarity.
    Returns the Path object of the best match or None.
    """
    best_match = None
    best_score = 0
    
    # Clean app name for comparison
    clean_app_name = clean_name_for_comparison(app_name)
    
    for exe_file in exe_files:
        exe_name = clean_name_for_comparison(exe_file.stem)
        
        # Calculate similarity score
        similarity = SequenceMatcher(None, clean_app_name, exe_name).ratio()
        
        # Additional scoring for common patterns
        if exe_name in clean_app_name or clean_app_name in exe_name:
            similarity += 0.3  # Bonus for substring matches
        
        if similarity > best_score:
            best_score = similarity
            best_match = exe_file
    
    # Only return if similarity is above threshold
    return best_match if best_score > 0.3 else None

def clean_name_for_comparison(name: str) -> str:
    """
    Clean name for similarity comparison.
    """
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

def save_exe_apps_to_config(exe_apps: dict):
    """
    Saves the .exe apps mapping to a JSON config file.
    """
    with open('exe_apps_from_registry.json', 'w', encoding='utf-8') as f:
        json.dump(exe_apps, f, indent=2)
    print(f"Saved {len(exe_apps)} .exe applications to {'exe_apps_from_registry.json'}")
