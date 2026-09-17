"""
Core functionality for extracting and repackaging PowerPoint files.

This module provides the essential functions for working with PowerPoint (.pptx) files
at the XML level. PowerPoint files are essentially ZIP archives containing XML files
that define the presentation structure, content, and formatting.

The module supports:
- Extracting .pptx files into directory structures for inspection/editing
- Repackaging modified directories back into working .pptx files
- Optional XML prettification for improved readability

Functions:
    unpptx_file: Extract a PowerPoint file into component XML/media files
    dopptx_folder: Repackage an extracted directory back into a .pptx file

Note:
    This module uses Python's logging module for debug/info messages. By default,
    these are not displayed. To enable logging output when using this module
    programmatically, configure the logging module before calling these functions.

"""

import logging
import xml.dom.minidom
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Compression level used when creating .pptx files (ZIP_DEFLATED provides good compression)
_COMPRESSION_LEVEL = zipfile.ZIP_DEFLATED


def unpptx_file(pptx_folder: Path, pptx_file: Path, *, pretty: bool) -> None:
    """
    Extract a single PowerPoint file into its component XML and media files.

    This function decompresses a .pptx file (which is essentially a ZIP archive)
    into a directory structure that mirrors the internal organization of the
    PowerPoint file. The extracted content includes XML files defining slides,
    layouts, themes, relationships, and any embedded media.

    Args:
        pptx_folder: The parent directory where the extracted folder will be created.
        pptx_file: Path to the PowerPoint (.pptx) file to extract.
        pretty: If True, formats all XML files with proper indentation and line
                breaks for improved readability. This makes the files easier to
                inspect and edit manually, but may increase file size slightly.

    Returns:
        None: The function creates a directory named "{pptx_file.stem}_pptx"
              containing all extracted files.

    Raises:
        ValueError: If the file is not a valid PowerPoint file or has wrong extension.
        FileNotFoundError: If the specified pptx_file does not exist.

    Example:
        >>> from pathlib import Path
        >>> unpptx_file(Path("/presentations"), Path("/presentations/demo.pptx"), pretty=True)
        # Creates: /presentations/demo_pptx/ with all extracted content

    Note:
        The extracted directory structure follows the Open Packaging Conventions
        used by Microsoft Office documents, including:
        - ppt/slides/ - Individual slide definitions
        - ppt/slideLayouts/ - Slide layout templates
        - ppt/slideMasters/ - Master slide definitions
        - ppt/theme/ - Theme and styling information
        - _rels/ - Relationship mappings between components
        - [Content_Types].xml - MIME type definitions

    """
    logger.debug(f"Starting extraction of {pptx_file}")

    if not pptx_file.exists():
        logger.error(f"File not found: {pptx_file}")
        raise FileNotFoundError(f"File not found: {pptx_file}")

    if pptx_file.suffix.lower() != ".pptx":
        logger.error(f"Invalid file extension: {pptx_file.suffix}")
        raise ValueError(f"File must have .pptx extension, got {pptx_file.suffix}")

    output_folder = Path(pptx_folder) / f"{pptx_file.stem}_pptx"
    logger.info(f"Extracting {pptx_file.name} to {output_folder}")

    try:
        with zipfile.ZipFile(pptx_file, "r") as zip_ref:
            zip_ref.extractall(output_folder)
        logger.info(f"Successfully extracted {len(list(output_folder.rglob('*')))} items")
    except zipfile.BadZipFile as e:
        logger.error(f"Invalid PowerPoint file: {pptx_file}")
        raise ValueError(f"{pptx_file} is not a valid PowerPoint file") from e

    def prettify_files(pattern: str) -> None:
        """
        Format XML files with proper indentation for readability.

        Args:
            pattern: Glob pattern to match files for prettification (e.g., "**/*.xml").

        """
        files = list(output_folder.glob(pattern))
        logger.debug(f"Prettifying {len(files)} files matching pattern '{pattern}'")
        for xml_file in files:
            with open(xml_file) as f:
                xml_string = f.read()
                dom = xml.dom.minidom.parseString(xml_string)
                pretty_xml_as_string = dom.toprettyxml()
            with open(xml_file, "w") as f:
                f.write(pretty_xml_as_string)

    if pretty:
        logger.debug("Prettifying XML and rels files")
        prettify_files("**/*.xml")
        prettify_files("**/*.rels")


def dopptx_folder(pptx_folder: Path, pptx_exploded_folder: Path) -> None:
    """
    Repackage an extracted PowerPoint directory back into a .pptx file.

    This function takes a directory containing extracted PowerPoint components
    (XML files, media, etc.) and compresses them back into a functional .pptx
    file. The directory structure must follow the Open Packaging Conventions
    format as created by the unpptx_file function.

    Args:
        pptx_folder: The parent directory where the new .pptx file will be created.
        pptx_exploded_folder: Path to the directory containing extracted PowerPoint
                             components. Must end with "_pptx" suffix and contain
                             the proper internal structure.

    Returns:
        None: The function creates a .pptx file in the pptx_folder directory.

    Raises:
        ValueError: If the folder doesn't end with "_pptx" suffix.
        FileNotFoundError: If the exploded folder doesn't exist.

    Example:
        >>> from pathlib import Path
        >>> dopptx_folder(Path("/presentations"), Path("/presentations/demo_pptx"))
        # Creates: /presentations/demo.pptx

    Note:
        The function automatically determines the output filename by removing the
        "_pptx" suffix from the exploded folder name. All files and subdirectories
        in the exploded folder are included in the final .pptx archive with
        ZIP_DEFLATED compression.

    """
    logger.debug(f"Starting repackaging of {pptx_exploded_folder}")

    if not pptx_exploded_folder.exists():
        logger.error(f"Folder not found: {pptx_exploded_folder}")
        raise FileNotFoundError(f"Folder not found: {pptx_exploded_folder}")

    if not pptx_exploded_folder.name.endswith("_pptx"):
        logger.error(f"Folder must end with '_pptx' suffix: {pptx_exploded_folder.name}")
        raise ValueError(f"Folder must end with '_pptx' suffix, got {pptx_exploded_folder.name}")

    deck_name = pptx_exploded_folder.stem[:-5]
    pptx_file = Path(pptx_folder) / f"{deck_name}.pptx"
    logger.info(f"Repackaging {pptx_exploded_folder.name} to {pptx_file.name}")

    file_count = 0
    with zipfile.ZipFile(pptx_file, "w") as zip_ref:
        for file in pptx_exploded_folder.glob("**/*"):
            if file.is_dir():
                continue
            zip_ref.write(file, file.relative_to(pptx_exploded_folder), compress_type=_COMPRESSION_LEVEL)
            file_count += 1

    logger.info(f"Successfully created {pptx_file.name} with {file_count} files")
