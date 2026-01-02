import json
import shutil
import logging
from pathlib import Path
from PyQt5.QtCore import QMutexLocker
from src.core import config
from src.features import functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reorganize_by_extension(project_dir: str = ''):
    """
    Scans 'root' for all files,
    groups them by extension, and moves each
    file into a folder named after that extension.
    """
    project_dir = Path(project_dir)

    # Dict for relocation logging
    relocation_log = {}

    # Iterate over every item in project_dir
    for item in project_dir.iterdir():
        if item.is_file():
            extension = item.suffix.lower().lstrip('.') or 'no_ext'
            target_dir = project_dir / extension

            # Ensure the target directory exists (creates ones, if doesn't)
            target_dir.mkdir(exist_ok=True)

            # Build the destination path
            destination = target_dir / item.name

            # Move the file
            shutil.move(str(item), str(destination))

            # Record in the log
            relocation_log[item.name] = str(destination.relative_to(project_dir))

    logger.info('Relocation is completed')
    functions.run_message_formater('Relocation is completed')

    # Create paths for logs json
    logs_path = project_dir / 'relocation_log.json'
    try:
        with open(logs_path, 'w') as file:
            json.dump(relocation_log, file, indent=2)
            logger.info('Logs were saved')
    except Exception as e:
        logger.error(f'Error occurs while trying to save relocation logs: {str(e)}')

if __name__ == '__main__':
    project_dir = input('Write the directory that you want to reorginize:\n')
    reorganize_by_extension(project_dir)