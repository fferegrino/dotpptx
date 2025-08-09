import filecmp
import zipfile
from pathlib import Path


def assert_folders_are_equal(folder1: Path, folder2: Path) -> None:
    """
    Recursively compare two folders to check if they contain the same files and folders.

    Args:
        folder1: Path to the first folder
        folder2: Path to the second folder

    Raises:
        AssertionError: If folders are not identical

    """
    # Check if both paths exist and are directories
    if not folder1.exists() or not folder2.exists():
        raise AssertionError(f"Folders {folder1} and {folder2} do not exist")

    if not folder1.is_dir() or not folder2.is_dir():
        raise AssertionError(f"Folders {folder1} and {folder2} are not directories")

    # Get all files and directories in both folders recursively
    def get_all_relative_paths(base_path: Path) -> set[Path]:
        return {item.relative_to(base_path) for item in base_path.rglob("*") if item.is_file()}

    files1 = get_all_relative_paths(folder1)
    files2 = get_all_relative_paths(folder2)

    # Check if the sets of files are the same
    if files1 != files2:
        missing_in_2 = files1 - files2
        missing_in_1 = files2 - files1
        error_msg = f"Folders {folder1} and {folder2} have different files."
        if missing_in_2:
            error_msg += f" Missing in {folder2}: {missing_in_2}"
        if missing_in_1:
            error_msg += f" Missing in {folder1}: {missing_in_1}"
        raise AssertionError(error_msg)

    # Compare file contents

    for relative_file in files1:
        file1 = folder1 / relative_file
        file2 = folder2 / relative_file
        if not filecmp.cmp(file1, file2, shallow=False):
            raise AssertionError(f"Files {file1} and {file2} have different contents")


def assert_zip_files_are_equal(file1: Path, file2: Path) -> bool:
    """
    Compare two zip files to check if they contain the same files and folders.

    Args:
        file1: Path to the first zip file
        file2: Path to the second zip file

    Returns:
        bool: True if zip files are equal, False otherwise

    """
    with zipfile.ZipFile(file1, "r") as zip_ref:
        actual_filelist = sorted(zip_ref.filelist, key=lambda x: x.filename)
    with zipfile.ZipFile(file2, "r") as zip_ref:
        expected_filelist = sorted(zip_ref.filelist, key=lambda x: x.filename)

    if len(actual_filelist) != len(expected_filelist):
        assert False, f"Files {file1} and {file2} have different number of files"

    for actual_file, expected_file in zip(actual_filelist, expected_filelist, strict=False):
        if actual_file.filename != expected_file.filename:
            assert False, f"Files {file1} and {file2} have different files"
        if actual_file.file_size != expected_file.file_size:
            assert False, f"Files {file1} and {file2} have different file sizes"
