import winreg
import json
import os
from extract_exe import find_exe_files, save_exe_apps_to_config

# List of registry hives and paths to search for installed applications
REGISTRY_PATHS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]

def scan_registry_for_apps():
    """
    Scans Windows uninstall registry keys for installed applications.
    Returns a dict mapping application display names to executable paths.
    """
    apps = {}
    for hive, path in REGISTRY_PATHS:
        try:
            with winreg.OpenKey(hive, path) as reg_key:
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(reg_key, i)
                        with winreg.OpenKey(hive, f"{path}\{subkey_name}") as subkey:
                            # Read DisplayName
                            display_name, _ = winreg.QueryValueEx(subkey, 'DisplayName')
                            # Try to read InstallLocation or DisplayIcon
                            try:
                                install_location, _ = winreg.QueryValueEx(subkey, 'InstallLocation')
                                exe_path = install_location
                            except FileNotFoundError:
                                try:
                                    display_icon, _ = winreg.QueryValueEx(subkey, 'DisplayIcon')
                                    exe_path = display_icon
                                except FileNotFoundError:
                                    continue
                            # Only record if path exists
                            if exe_path and os.path.exists(exe_path):
                                apps[display_name] = exe_path
                    except (FileNotFoundError, OSError, PermissionError):
                        # Skip entries we can't access or without the right values
                        continue
        except (FileNotFoundError, PermissionError):
            continue

    save_apps_to_config(apps)
    return apps

def save_apps_to_config(apps: dict):
    """
    Saves the apps mapping to a JSON config file in the EVA config directory.
    """
    with open('result_of_registry_scan.json', 'w', encoding='utf-8') as f:
        json.dump(apps, f, indent=2)
    print(f"Saved {len(apps)} applications to {'result_of_registry_scan.json'}")

if __name__ == '__main__':
    # Test the scanner
    found_apps = scan_registry_for_apps()
    print(f"Found {len(found_apps)} total applications")
