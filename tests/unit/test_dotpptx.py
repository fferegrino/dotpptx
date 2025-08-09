from pathlib import Path

import pytest

from dotpptx.dotpptx import dopptx_folder, unpptx_file
from tests.helpers import assert_folders_are_equal, assert_zip_files_are_equal


def test_unpptx_file(tmp_path: Path, pytestconfig: pytest.Config):
    unpptx_file(tmp_path, Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx", pretty=False)
    assert_folders_are_equal(tmp_path / "slides-1_pptx", Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx")


def test_dopptx_folder(tmp_path: Path, pytestconfig: pytest.Config):
    output_folder = tmp_path
    dopptx_folder(tmp_path, Path(pytestconfig.rootdir) / "tests/fixtures/slides-1_pptx")

    actual_slides = output_folder / "slides-1.pptx"
    expected_slides = Path(pytestconfig.rootdir) / "tests/fixtures/slides-1.pptx"

    assert_zip_files_are_equal(actual_slides, expected_slides)
