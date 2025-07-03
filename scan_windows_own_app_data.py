import logging
from scanner_registry import scan_registry_for_apps
from scanner_shortcut import scan_shortcuts_for_apps
from extract_exe import find_exe_files
from deduplicate_apps import start_deduplication

logger = logging.getLogger(__name__)

def start_scan():
    # Scan shortcuts and registry
    scan_shortcuts_for_apps()
    registry_apps = scan_registry_for_apps()

    # Extract .exe files from registry apps
    find_exe_files(registry_apps)

    # Define sources for deduplication
    sources = [
        'result_of_shortcuts_scan.json',
        'exe_apps_from_registry.json'
    ]

    # Run deduplication
    start_deduplication(sources=sources)

    logger.info('Scaning for Applications in Windows own data is complited')

if __name__ == '__main__':
    start_scan()