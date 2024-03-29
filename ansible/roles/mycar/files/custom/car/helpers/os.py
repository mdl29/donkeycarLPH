import logging
import os, shutil
import tarfile
from pathlib import Path

from typing_extensions import NoReturn


def clean_directory_content(folder: str) -> NoReturn:
    """
    Clean a directory content without removing the directory
    :param folder: folder path.
    """
    logger = logging.getLogger( __name__  + ".clean_directory_content")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error('Failed to delete %s. Reason: ', file_path)
            logger.exception(e)


def uncompress_tarfile(input_filename, output_folder) -> NoReturn:
    """
    Uncomrpess a tar file into a destination directory.
    :param input_filename:
    :param output_folder:
    """
    with tarfile.open(input_filename, "r:gz") as tar:
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        tar.extractall(output_folder)


def make_tarfile(output_filename, source_dir) -> NoReturn:
    """
    Make a tar file from a directory.
    :param output_filename: Output file path.
    :param source_dir: Source directory
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
