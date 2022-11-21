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

        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, output_folder)

def make_tarfile(output_filename, source_dir) -> NoReturn:
    """
    Make a tar file from a directory.
    :param output_filename: Output file path.
    :param source_dir: Source directory
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
