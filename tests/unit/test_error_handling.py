"""Tests for error handling in dotpptx."""
from pathlib import Path

import pytest

from dotpptx.dotpptx import dopptx_folder, unpptx_file


class TestUnpptxFileErrorHandling:
    """Test error handling in unpptx_file function."""

    def test_unpptx_file_not_found(self, tmp_path: Path):
        """Test that unpptx_file raises FileNotFoundError for non-existent file."""
        nonexistent_file = tmp_path / "nonexistent.pptx"

        with pytest.raises(FileNotFoundError, match="File not found"):
            unpptx_file(tmp_path, nonexistent_file, pretty=False)

    def test_unpptx_invalid_extension(self, tmp_path: Path):
        """Test that unpptx_file raises ValueError for non-.pptx file."""
        invalid_file = tmp_path / "document.txt"
        invalid_file.touch()

        with pytest.raises(ValueError, match="File must have .pptx extension"):
            unpptx_file(tmp_path, invalid_file, pretty=False)

    def test_unpptx_invalid_extension_uppercase(self, tmp_path: Path):
        """Test that unpptx_file raises ValueError for uppercase non-.pptx file."""
        invalid_file = tmp_path / "document.TXT"
        invalid_file.touch()

        with pytest.raises(ValueError, match="File must have .pptx extension"):
            unpptx_file(tmp_path, invalid_file, pretty=False)

    def test_unpptx_valid_extension_case_insensitive(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test that .PPTX (uppercase) extension is accepted."""
        # Create a valid pptx file with uppercase extension
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        test_file = tmp_path / "TEST.PPTX"

        # Copy the fixture with uppercase extension
        import shutil

        shutil.copy2(fixture_file, test_file)

        # Should not raise an error
        unpptx_file(tmp_path, test_file, pretty=False)

        # Verify extraction occurred
        assert (tmp_path / "TEST_pptx").exists()

    def test_unpptx_invalid_zip_file(self, tmp_path: Path):
        """Test that unpptx_file raises ValueError for invalid zip/pptx file."""
        invalid_pptx = tmp_path / "invalid.pptx"
        invalid_pptx.write_text("This is not a valid PowerPoint file")

        with pytest.raises(ValueError, match="not a valid PowerPoint file"):
            unpptx_file(tmp_path, invalid_pptx, pretty=False)

    def test_unpptx_empty_file(self, tmp_path: Path):
        """Test that unpptx_file raises ValueError for empty file."""
        empty_file = tmp_path / "empty.pptx"
        empty_file.touch()

        with pytest.raises(ValueError, match="not a valid PowerPoint file"):
            unpptx_file(tmp_path, empty_file, pretty=False)


class TestDopptxFolderErrorHandling:
    """Test error handling in dopptx_folder function."""

    def test_dopptx_folder_not_found(self, tmp_path: Path):
        """Test that dopptx_folder raises FileNotFoundError for non-existent folder."""
        nonexistent_folder = tmp_path / "nonexistent_pptx"

        with pytest.raises(FileNotFoundError, match="Folder not found"):
            dopptx_folder(tmp_path, nonexistent_folder)

    def test_dopptx_invalid_folder_name(self, tmp_path: Path):
        """Test that dopptx_folder raises ValueError for folder without _pptx suffix."""
        invalid_folder = tmp_path / "presentation"
        invalid_folder.mkdir()

        with pytest.raises(ValueError, match="Folder must end with '_pptx' suffix"):
            dopptx_folder(tmp_path, invalid_folder)

    def test_dopptx_folder_is_file(self, tmp_path: Path):
        """Test that dopptx_folder raises error when path is a file, not a folder."""
        file_path = tmp_path / "not_a_folder_pptx"
        file_path.touch()

        with pytest.raises(ValueError, match="Path must be a directory"):
            dopptx_folder(tmp_path, file_path)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unpptx_with_special_characters_in_filename(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test extraction with special characters in filename."""
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        import shutil

        # Test with spaces and dashes
        test_file = tmp_path / "my-presentation 2024.pptx"
        shutil.copy2(fixture_file, test_file)

        unpptx_file(tmp_path, test_file, pretty=False)

        assert (tmp_path / "my-presentation 2024_pptx").exists()

    def test_unpptx_preserves_folder_structure(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test that extraction preserves the internal folder structure."""
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        import shutil

        test_file = tmp_path / "test.pptx"
        shutil.copy2(fixture_file, test_file)

        unpptx_file(tmp_path, test_file, pretty=False)

        output_folder = tmp_path / "test_pptx"

        # Check that key folders exist
        assert (output_folder / "ppt").exists()
        assert (output_folder / "ppt" / "slides").exists()
        assert (output_folder / "_rels").exists()

    def test_dopptx_creates_valid_zip(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test that dopptx creates a valid ZIP/PPTX file."""
        import shutil
        import zipfile

        fixture_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"
        test_folder = tmp_path / "test_pptx"
        shutil.copytree(fixture_folder, test_folder)

        dopptx_folder(tmp_path, test_folder)

        output_file = tmp_path / "test.pptx"
        assert output_file.exists()
        assert zipfile.is_zipfile(output_file)

    def test_unpptx_output_folder_already_exists(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test behavior when output folder already exists (should overwrite)."""
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        import shutil

        test_file = tmp_path / "test.pptx"
        shutil.copy2(fixture_file, test_file)

        # Create the output folder with some content
        output_folder = tmp_path / "test_pptx"
        output_folder.mkdir()
        (output_folder / "dummy.txt").write_text("This should remain")

        # Extract should succeed
        unpptx_file(tmp_path, test_file, pretty=False)

        # Output folder should exist with extracted content
        assert output_folder.exists()
        assert (output_folder / "ppt").exists()
        # Original dummy file might still exist since we extract to the same location
