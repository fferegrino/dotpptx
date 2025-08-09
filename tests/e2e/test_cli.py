import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from tests.helpers import assert_folders_are_equal


def run_cli_command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """
    Run a dotpptx CLI command and return the result.

    Args:
        args: Command line arguments
        cwd: Working directory for the command

    Returns:
        CompletedProcess with the result

    """
    cmd = [sys.executable, "-m", "dotpptx"] + args
    return subprocess.run(cmd, check=False, capture_output=True, text=True, cwd=cwd)


class TestUnpptxCommand:
    """Test the unpptx command functionality."""

    def test_unpptx_single_file(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test unpptx command on a single PowerPoint file."""
        # Copy fixture to temp directory
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        test_pptx = tmp_path / "slides-1.pptx"
        shutil.copy2(fixture_file, test_pptx)

        # Run unpptx command
        result = run_cli_command(["unpptx", str(test_pptx)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that the extracted folder was created
        extracted_folder = tmp_path / "slides-1_pptx"
        assert extracted_folder.exists(), "Extracted folder should exist"
        assert extracted_folder.is_dir(), "Extracted folder should be a directory"

        # Compare with expected structure
        expected_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"
        assert_folders_are_equal(extracted_folder, expected_folder)

    def test_unpptx_single_file_pretty(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test unpptx command with --pretty flag on a single PowerPoint file."""
        # Copy fixture to temp directory
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        test_pptx = tmp_path / "slides-1.pptx"
        shutil.copy2(fixture_file, test_pptx)

        # Run unpptx command with --pretty
        result = run_cli_command(["unpptx", "--pretty", str(test_pptx)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that the extracted folder was created
        extracted_folder = tmp_path / "slides-1_pptx"
        assert extracted_folder.exists(), "Extracted folder should exist"
        assert extracted_folder.is_dir(), "Extracted folder should be a directory"

        # Check that XML files are prettified (they should be formatted differently)
        xml_files = list(extracted_folder.glob("**/*.xml"))
        assert len(xml_files) > 0, "Should have XML files"

        # Verify at least one XML file has proper formatting (indentation)
        sample_xml = xml_files[0]
        content = sample_xml.read_text()
        assert "\n" in content, "Pretty XML should have newlines"
        # Check for XML declaration which is added by minidom
        assert content.startswith("<?xml"), "Pretty XML should start with XML declaration"

    def test_unpptx_directory_with_multiple_files(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test unpptx command on a directory containing multiple PowerPoint files."""
        # Copy fixture multiple times with different names
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"

        test_dir = tmp_path / "pptx_files"
        test_dir.mkdir()

        test_files = [test_dir / "presentation1.pptx", test_dir / "presentation2.pptx", test_dir / "report.pptx"]

        for test_file in test_files:
            shutil.copy2(fixture_file, test_file)

        # Run unpptx command on directory
        result = run_cli_command(["unpptx", str(test_dir)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that all extracted folders were created
        expected_folders = [test_dir / "presentation1_pptx", test_dir / "presentation2_pptx", test_dir / "report_pptx"]

        for folder in expected_folders:
            assert folder.exists(), f"Extracted folder {folder} should exist"
            assert folder.is_dir(), f"Extracted folder {folder} should be a directory"

    def test_unpptx_directory_skips_temp_files(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test that unpptx skips PowerPoint temporary files (starting with ~$)."""
        # Copy fixture and create a temp file
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"

        test_dir = tmp_path / "pptx_files"
        test_dir.mkdir()

        normal_file = test_dir / "presentation.pptx"
        temp_file = test_dir / "~$presentation.pptx"

        shutil.copy2(fixture_file, normal_file)
        shutil.copy2(fixture_file, temp_file)

        # Run unpptx command
        result = run_cli_command(["unpptx", str(test_dir)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that only the normal file was processed
        assert (test_dir / "presentation_pptx").exists(), "Normal file should be extracted"
        assert not (test_dir / "~$presentation_pptx").exists(), "Temp file should be skipped"

    def test_unpptx_nonexistent_file(self, tmp_path: Path):
        """Test unpptx command with a non-existent file."""
        nonexistent_file = tmp_path / "nonexistent.pptx"

        result = run_cli_command(["unpptx", str(nonexistent_file)], cwd=tmp_path)

        # Command should fail
        assert result.returncode != 0, "Command should fail for non-existent file"


class TestDopptxCommand:
    """Test the dopptx command functionality."""

    def test_dopptx_single_folder(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test dopptx command on a single exploded PowerPoint folder."""
        # Copy fixture folder to temp directory
        fixture_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"
        test_folder = tmp_path / "slides-1_pptx"
        shutil.copytree(fixture_folder, test_folder)

        # Run dopptx command
        result = run_cli_command(["dopptx", str(test_folder)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that the PPTX file was created
        output_pptx = tmp_path / "slides-1.pptx"
        assert output_pptx.exists(), "Output PPTX file should exist"
        assert output_pptx.is_file(), "Output should be a file"

        # Verify it's a valid ZIP file (PPTX is a ZIP)
        assert zipfile.is_zipfile(output_pptx), "Output should be a valid ZIP/PPTX file"

        # Compare with original fixture
        original_pptx = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"

        # Compare zip contents
        with zipfile.ZipFile(output_pptx, "r") as output_zip:
            output_files = sorted(output_zip.namelist())

        with zipfile.ZipFile(original_pptx, "r") as original_zip:
            original_files = sorted(original_zip.namelist())

        assert output_files == original_files, "ZIP contents should match original"

    def test_dopptx_single_folder_with_delete_original(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test dopptx command with --delete-original flag."""
        # Copy fixture folder to temp directory
        fixture_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"
        test_folder = tmp_path / "slides-1_pptx"
        shutil.copytree(fixture_folder, test_folder)

        # Verify folder exists before
        assert test_folder.exists(), "Test folder should exist before command"

        # Run dopptx command with delete flag
        result = run_cli_command(["dopptx", "--delete-original", str(test_folder)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that the PPTX file was created
        output_pptx = tmp_path / "slides-1.pptx"
        assert output_pptx.exists(), "Output PPTX file should exist"

        # Check that original folder was deleted
        assert not test_folder.exists(), "Original folder should be deleted"

    def test_dopptx_directory_with_multiple_folders(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test dopptx command on a directory containing multiple exploded PowerPoint folders."""
        # Copy fixture folder multiple times with different names
        fixture_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"

        test_dir = tmp_path / "presentations"
        test_dir.mkdir()

        folder_names = ["presentation1_pptx", "presentation2_pptx", "report_pptx"]

        for folder_name in folder_names:
            shutil.copytree(fixture_folder, test_dir / folder_name)

        # Run dopptx command on directory
        result = run_cli_command(["dopptx", str(test_dir)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that all PPTX files were created
        expected_files = [test_dir / "presentation1.pptx", test_dir / "presentation2.pptx", test_dir / "report.pptx"]

        for pptx_file in expected_files:
            assert pptx_file.exists(), f"PPTX file {pptx_file} should exist"
            assert pptx_file.is_file(), f"{pptx_file} should be a file"

            assert zipfile.is_zipfile(pptx_file), f"{pptx_file} should be a valid ZIP/PPTX file"

    def test_dopptx_directory_with_delete_original(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test dopptx command on directory with --delete-original flag."""
        # Copy fixture folder multiple times
        fixture_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"

        test_dir = tmp_path / "presentations"
        test_dir.mkdir()

        folder_names = ["presentation1_pptx", "presentation2_pptx"]
        test_folders = []

        for folder_name in folder_names:
            folder_path = test_dir / folder_name
            shutil.copytree(fixture_folder, folder_path)
            test_folders.append(folder_path)

        # Verify folders exist before
        for folder in test_folders:
            assert folder.exists(), f"Test folder {folder} should exist before command"

        # Run dopptx command with delete flag
        result = run_cli_command(["dopptx", "--delete-original", str(test_dir)], cwd=tmp_path)

        # Assert command succeeded
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that PPTX files were created and folders were deleted
        for i, folder_name in enumerate(folder_names):
            pptx_file = test_dir / f"{folder_name[:-5]}.pptx"  # Remove "_pptx" suffix
            assert pptx_file.exists(), f"PPTX file {pptx_file} should exist"
            assert not test_folders[i].exists(), f"Original folder {test_folders[i]} should be deleted"

    def test_dopptx_nonexistent_folder(self, tmp_path: Path):
        """Test dopptx command with a non-existent folder."""
        nonexistent_folder = tmp_path / "nonexistent_pptx"

        result = run_cli_command(["dopptx", str(nonexistent_folder)], cwd=tmp_path)

        # Command should fail
        assert result.returncode != 0, "Command should fail for non-existent folder"

    def test_dopptx_folder_without_pptx_suffix(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test dopptx command on a folder without _pptx suffix (should be ignored)."""
        # Copy fixture folder with different name (no _pptx suffix)
        fixture_folder = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx"
        test_folder = tmp_path / "slides-1"  # No _pptx suffix
        shutil.copytree(fixture_folder, test_folder)

        # Run dopptx command
        result = run_cli_command(["dopptx", str(test_folder)], cwd=tmp_path)

        # Command should succeed but do nothing
        assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"

        # Check that no PPTX file was created
        output_pptx = tmp_path / "slides-1.pptx"
        assert not output_pptx.exists(), "No PPTX file should be created for folder without _pptx suffix"


class TestRoundTripWorkflow:
    """Test complete round-trip workflows: PPTX -> folder -> PPTX."""

    def test_unpptx_then_dopptx_roundtrip(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test complete round-trip: extract PPTX to folder, then rebuild PPTX."""
        # Copy original fixture
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        original_pptx = tmp_path / "original.pptx"
        shutil.copy2(fixture_file, original_pptx)

        # Step 1: Extract PPTX to folder
        result1 = run_cli_command(["unpptx", str(original_pptx)], cwd=tmp_path)
        assert result1.returncode == 0, f"Unpptx failed with stderr: {result1.stderr}"

        extracted_folder = tmp_path / "original_pptx"
        assert extracted_folder.exists(), "Extracted folder should exist"

        # Step 2: Rebuild PPTX from folder
        result2 = run_cli_command(["dopptx", str(extracted_folder)], cwd=tmp_path)
        assert result2.returncode == 0, f"Dopptx failed with stderr: {result2.stderr}"

        rebuilt_pptx = tmp_path / "original.pptx"
        assert rebuilt_pptx.exists(), "Rebuilt PPTX should exist"

        # Step 3: Verify round-trip integrity
        # Compare ZIP file contents
        with zipfile.ZipFile(fixture_file, "r") as original_zip:
            original_files = sorted(original_zip.namelist())

        with zipfile.ZipFile(rebuilt_pptx, "r") as rebuilt_zip:
            rebuilt_files = sorted(rebuilt_zip.namelist())

        assert original_files == rebuilt_files, "Round-trip should preserve all files"

    def test_unpptx_pretty_then_dopptx_roundtrip(self, tmp_path: Path, pytestconfig: pytest.Config):
        """Test round-trip with pretty formatting."""
        # Copy original fixture
        fixture_file = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"
        original_pptx = tmp_path / "original.pptx"
        shutil.copy2(fixture_file, original_pptx)

        # Step 1: Extract PPTX to folder with pretty formatting
        result1 = run_cli_command(["unpptx", "--pretty", str(original_pptx)], cwd=tmp_path)
        assert result1.returncode == 0, f"Unpptx failed with stderr: {result1.stderr}"

        extracted_folder = tmp_path / "original_pptx"
        assert extracted_folder.exists(), "Extracted folder should exist"

        # Step 2: Rebuild PPTX from prettified folder
        result2 = run_cli_command(["dopptx", str(extracted_folder)], cwd=tmp_path)
        assert result2.returncode == 0, f"Dopptx failed with stderr: {result2.stderr}"

        rebuilt_pptx = tmp_path / "original.pptx"
        assert rebuilt_pptx.exists(), "Rebuilt PPTX should exist"

        # Step 3: Verify the rebuilt PPTX is valid
        assert zipfile.is_zipfile(rebuilt_pptx), "Rebuilt PPTX should be a valid ZIP file"

        # Note: We don't expect exact binary match because pretty formatting changes XML
        # but we verify structural integrity
        with zipfile.ZipFile(rebuilt_pptx, "r") as rebuilt_zip:
            rebuilt_files = sorted(rebuilt_zip.namelist())

        with zipfile.ZipFile(fixture_file, "r") as original_zip:
            original_files = sorted(original_zip.namelist())

        assert rebuilt_files == original_files, "Pretty round-trip should preserve file structure"


class TestCLIHelp:
    """Test CLI help and error handling."""

    def test_cli_help(self):
        """Test that CLI shows help information."""
        result = run_cli_command(["--help"])
        assert result.returncode == 0, "Help command should succeed"
        assert "Usage:" in result.stdout, "Help should show usage information"

    def test_unpptx_help(self):
        """Test unpptx command help."""
        result = run_cli_command(["unpptx", "--help"])
        assert result.returncode == 0, "Unpptx help command should succeed"
        assert "Usage:" in result.stdout, "Help should show usage information"
        assert "pretty" in result.stdout, "Help should mention pretty flag"

    def test_dopptx_help(self):
        """Test dopptx command help."""
        result = run_cli_command(["dopptx", "--help"])
        assert result.returncode == 0, "Dopptx help command should succeed"
        assert "Usage:" in result.stdout, "Help should show usage information"
        assert "delete-original" in result.stdout, "Help should mention delete-original flag"
