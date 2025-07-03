import os
import json
from pathlib import Path

# Requires pywin32: pip install pywin32
import pythoncom
from win32com.shell import shell

# Start Menu directories to search for shortcuts
START_MENU_DIRS = [
    os.path.join(os.getenv('PROGRAMDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
    os.path.join(os.getenv('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
]

def resolve_shortcut(lnk_path: str) -> str:
    """
    Resolve a .lnk shortcut to its target executable path.
    Returns the path or None if resolution fails.
    """
    try:
        pythoncom.CoInitialize()
        shell_link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
        )
        persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Load(lnk_path)
        # SLGP_RAWPATH to get raw target path
        target, _ = shell_link.GetPath(shell.SLGP_RAWPATH)
        return target
    except Exception:
        return None
    finally:
        pythoncom.CoUninitialize()


def scan_shortcuts_for_apps() -> dict:
    """
    Scans Start Menu directories for .lnk shortcuts and resolves them.
    Returns a dict mapping shortcut names to target executable paths.
    """
    apps = {}
    for base_dir in START_MENU_DIRS:
        if not os.path.isdir(base_dir):
            continue
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.lnk'):
                    lnk_path = os.path.join(root, file)
                    exe_path = resolve_shortcut(lnk_path)
                    if exe_path and os.path.exists(exe_path):
                        name = Path(file).stem
                        apps[name] = exe_path

    save_shortcuts_to_config(apps)

def save_shortcuts_to_config(apps: dict):
    """
    Saves the shortcuts dict to a JSON file for EVA's configuration.
    """
    with open('result_of_shortcuts_scan.json', 'w', encoding='utf-8') as f:
        json.dump(apps, f, indent=2)
    print(f"Saved {len(apps)} shortcuts to {'result_of_shortcuts_scan.json'}")

if __name__ == '__main__':
    shortcuts = scan_shortcuts_for_apps()
