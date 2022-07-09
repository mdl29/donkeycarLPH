import tarfile
import os
from pathlib import Path
from typing_extensions import NoReturn


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
