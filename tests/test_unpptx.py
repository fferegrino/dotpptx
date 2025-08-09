import pytest
from dotpptx.dotpptx import unpptx_file, dopptx_folder
from pathlib import Path
import filecmp
import zipfile

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
    
    for actual_file, expected_file in zip(actual_filelist, expected_filelist):
        if actual_file.filename != expected_file.filename:
            assert False, f"Files {file1} and {file2} have different files"
        if actual_file.file_size != expected_file.file_size:
            assert False, f"Files {file1} and {file2} have different file sizes"

def assert_folders_are_equal(folder1: Path, folder2: Path) -> bool:
    """
    Recursively compare two folders to check if they contain the same files and folders.
    
    Args:
        folder1: Path to the first folder
        folder2: Path to the second folder
        
    Returns:
        bool: True if folders are identical, False otherwise
    """
    # Check if both paths exist and are directories
    if not folder1.exists() or not folder2.exists():
        assert False, f"Folders {folder1} and {folder2} do not exist"
    
    if not folder1.is_dir() or not folder2.is_dir():
        assert False, f"Folders {folder1} and {folder2} are not directories"
    
    # Get all files and directories in both folders
    items1 = set(item.name for item in folder1.iterdir())
    items2 = set(item.name for item in folder2.iterdir())
    
    # Check if the sets of items are the same
    if items1 != items2:
        assert False, f"Folders {folder1} and {folder2} have different items"
    
    # Compare each item
    for item_name in items1:
        item1 = folder1 / item_name
        item2 = folder2 / item_name
        
        # If both are files, compare their contents
        if item1.is_file() and item2.is_file():
            if not filecmp.cmp(item1, item2, shallow=False):
                assert False, f"Files {item1} and {item2} are different"
        # If both are directories, recursively compare them
        elif item1.is_dir() and item2.is_dir():
            assert_folders_are_equal(item1, item2)
        # If one is file and other is directory, they're different
        else:
            assert False, f"Files {item1} and {item2} are different"



def test_unpptx_file(tmp_path: Path, pytestconfig: pytest.Config):
    unpptx_file(tmp_path, Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx", pretty=False)
    assert_folders_are_equal(
        tmp_path / "slides-1_pptx", 
        Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx")
    
def test_dopptx_folder(tmp_path: Path, pytestconfig: pytest.Config):
    output_folder = tmp_path
    dopptx_folder(tmp_path, Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx")

    actual_slides = output_folder / "slides-1.pptx"
    expected_slides = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"

    assert_zip_files_are_equal(actual_slides, expected_slides)