import os
import tarfile


def create_dir(dir_path, mode=None):
    """
    Create a directory. If it already exists, allow it and swallow the exception.

    :param dir_path: the directory to create
    :type dir_path: str
    :param mode: the permissions to set dir_path to (ie: 0o700)
    :type mode: int(octal)|None
    """
    try:
        # Unfortunately, the exists_ok parameter does not do what it's supposed to do.
        os.makedirs(dir_path, exist_ok=True)
    except FileExistsError:
        pass

    if mode is not None:
        os.chmod(dir_path, mode)


def write_file(file_contents, file_path):
    """
    Write a string or byte string to a file.

    :param file_contents: The string or byte string to write
    :type file_contents: str | bytes
    :param file_path: The path of the file to write
    :type file_path: str
    """
    file_dir, _ = os.path.split(file_path)
    create_dir(file_dir)

    if type(file_contents) is bytes:
        open_kwargs = {}
        file_mode = 'wb'
    else:
        open_kwargs = {'encoding': 'utf-8'}  # This is necessary since UTF-8 is not the default on all systems.
        file_mode = 'w'

    with open(file_path, file_mode, **open_kwargs) as f:
        f.write(file_contents)


def extract_tar(archive_file, target_dir=None, delete=False):
    """

    :param archive_file:
    :type archive_file:
    :param target_dir:
    :type target_dir:
    :param delete:
    :type delete:
    :return:
    :rtype:
    """
    if not target_dir:
        target_dir, _ = os.path.split(archive_file)  # default to same directory as tar file

    try:
        with tarfile.open(archive_file, 'r:gz') as f:
            f.extractall(target_dir)
    finally:
        if delete:
            os.remove(archive_file)


# TODO(dtran): Remove this function once its uses are deprecated.
def compress_directory(target_dir, archive_filename):
    tar_file = os.path.join(
        target_dir,
        archive_filename
    )
    with tarfile.open(tar_file, 'w:gz') as tar:
        tar.add(target_dir, arcname=".")

    return tar_file


def compress_directories(target_dirs_to_archive_paths, tarfile_path):
    """
    Archive the specified directories
    :param target_dirs_to_archive_paths: mapping of directories to their intended path in the archive file.
    :type target_dirs_to_archive_paths: dict
    :param tarfile_path: the path of the resulting archive file
    :return:
    """
    with tarfile.open(tarfile_path, 'w:gz') as tar:
        for dir_path, archive_name in target_dirs_to_archive_paths.items():
            # Sanitize directory string
            target_dir = os.path.normpath(dir_path)

            tar.add(target_dir, arcname=archive_name)

def remove_invalid_path_characters(path):
    """
    :param path: the path that may contain invalid characters
    :type path: str
    :return: the path with the invalid characters removed
    :rtype: str
    """
    # Replace colons and dashes
    return path.replace(':', '').replace('-', '')
