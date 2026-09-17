"""
Command-line interface for dotpptx PowerPoint extraction and repackaging tool.

This module provides the CLI commands for working with PowerPoint (.pptx) files.
Users can extract presentations into XML components for inspection and editing,
then repackage them back into working .pptx files.

Commands:
    unpptx: Extract PowerPoint files into their component XML/media files
    dopptx: Repackage extracted directories back into .pptx files

The CLI supports both single-file operations and batch processing of multiple
files in a directory.

Logging:
    The CLI uses click.echo() for user-facing output and Python's logging module
    for debug/info messages. Use -v or -vv flags to enable logging output.
    Use --quiet to suppress all non-error output.
"""

import logging
import shutil
import sys
from pathlib import Path

import click

from dotpptx.dotpptx import dopptx_folder, unpptx_file


def setup_logging(verbose: int) -> None:
    """
    Configure logging based on verbosity level.

    Args:
        verbose: 0=WARNING, 1=INFO, 2=DEBUG

    """
    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity (-v for INFO, -vv for DEBUG)")
@click.pass_context
def cli(ctx: click.Context, verbose: int) -> None:
    """
    Dotpptx - PowerPoint file extraction and repackaging tool.

    A command-line utility for working with PowerPoint (.pptx) files at the XML level.
    This tool allows you to extract PowerPoint presentations into their component
    XML files for inspection and editing, then repackage them back into working
    .pptx files.

    Common workflows:
    1. Extract a presentation: unpptx presentation.pptx
    2. Edit the XML files as needed
    3. Repackage: dopptx presentation_pptx/

    This is particularly useful for:
    - Programmatic manipulation of presentations
    - Version control of presentation content
    - Debugging presentation issues
    - Bulk modifications across slides
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--pretty", is_flag=True, default=False, help="Format XML files with indentation")
@click.option("--quiet", is_flag=True, help="Suppress output messages")
@click.pass_context
def unpptx(ctx: click.Context, path: Path, pretty: bool, quiet: bool) -> None:  # noqa: FBT001, C901, D417
    """
    Extract PowerPoint (.pptx) files into their component parts.

    This command decompresses a PowerPoint presentation file into a directory structure
    that mirrors the internal organization of the .pptx file (which is essentially a
    ZIP archive). This allows you to examine and edit the underlying XML files that
    make up a PowerPoint presentation.

    The extracted folder will be named after the original file with a "_pptx" suffix.
    For example, "presentation.pptx" becomes "presentation_pptx/".

    Args:
        path: The path to a PowerPoint file (.pptx) to extract, or a directory
              containing multiple .pptx files to process in batch. Temporary files
              starting with "~$" are automatically skipped.
        pretty: If enabled, formats all XML files in the extracted content with
                proper indentation and line breaks for better readability. This
                makes the files easier to read and diff, but may increase file size.
        quiet: If enabled, suppresses all output messages except errors.

    Examples:
        Extract a single PowerPoint file:
            dotpptx unpptx presentation.pptx

        Extract all PowerPoint files in a directory with pretty formatting:
            dotpptx unpptx /path/to/presentations --pretty

        Extract with verbose logging:
            dotpptx -v unpptx presentation.pptx

        Extract silently:
            dotpptx unpptx --quiet presentation.pptx

    Note:
        The extracted files maintain the exact same structure as the original .pptx
        internal format, including _rels directories, XML files, and media content.

    """

    def process_file(pptx_file: Path) -> None:
        """Process a single file with user feedback."""
        try:
            if not quiet:
                click.echo(f"Extracting {pptx_file.name}...")

            unpptx_file(path if path.is_dir() else path.parent, pptx_file, pretty=pretty)

            if not quiet:
                output_folder = pptx_file.parent / f"{pptx_file.stem}_pptx"
                click.secho(f"✓ Created {output_folder.name}", fg="green")

        except Exception as e:
            click.secho(f"✗ Failed to extract {pptx_file.name}: {e}", fg="red", err=True)
            if ctx.obj.get("verbose", 0) > 0:
                raise
            sys.exit(1)

    if path.is_file():
        process_file(path)
    else:
        files = [f for f in path.glob("*.pptx") if not f.stem.startswith("~$")]

        if not files:
            if not quiet:
                click.echo("No .pptx files found in directory")
            return

        if not quiet:
            click.echo(f"Found {len(files)} PowerPoint file(s)")

        for pptx_file in files:
            process_file(pptx_file)

        if not quiet:
            click.secho(f"\n✓ Processed {len(files)} file(s)", fg="green", bold=True)


@cli.command()
@click.argument("pptx-folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--delete-original", is_flag=True, default=False, help="Delete source folder after repackaging")
@click.option("--quiet", is_flag=True, help="Suppress output messages")
@click.pass_context
def dopptx(ctx: click.Context, pptx_folder: Path, delete_original: bool, quiet: bool) -> None:  # noqa: FBT001, C901, D417
    """
    Repackage extracted PowerPoint directories back into .pptx files.

    This command takes directories that were previously extracted using the unpptx
    command and recompresses them back into functional PowerPoint (.pptx) files.
    This is useful after you've made modifications to the underlying XML structure
    of a presentation.

    The command can process either a single extracted directory (ending with "_pptx")
    or a parent directory containing multiple extracted directories.

    Args:
        pptx_folder: Path to either:
                    - A single extracted PowerPoint directory (ending with "_pptx")
                    - A parent directory containing multiple "*_pptx" directories
        delete_original: If enabled, removes the source directory after successfully
                        creating the .pptx file. Use with caution as this permanently
                        deletes the extracted files.
        quiet: If enabled, suppresses all output messages except errors.

    Examples:
        Repackage a single extracted directory:
            dotpptx dopptx presentation_pptx/

        Repackage all extracted directories in a folder:
            dotpptx dopptx /path/to/extracted_presentations/

        Repackage and clean up source directories:
            dotpptx dopptx presentation_pptx/ --delete-original

        Repackage with verbose logging:
            dotpptx -v dopptx presentation_pptx/

        Repackage silently:
            dotpptx dopptx --quiet presentation_pptx/

    Note:
        The resulting .pptx file will be created in the parent directory of the
        extracted folder, with the same base name as the original file.
        For example, "presentation_pptx/" becomes "presentation.pptx".

    """

    def process_folder(folder: Path) -> None:
        """Process a single folder with user feedback."""
        try:
            if not quiet:
                click.echo(f"Repackaging {folder.name}...")

            dopptx_folder(folder.parent, folder)

            output_file = folder.parent / f"{folder.stem[:-5]}.pptx"

            if delete_original:
                shutil.rmtree(folder)
                if not quiet:
                    click.secho(f"✓ Created {output_file.name} (original deleted)", fg="green")
            elif not quiet:
                click.secho(f"✓ Created {output_file.name}", fg="green")

        except Exception as e:
            click.secho(f"✗ Failed to repackage {folder.name}: {e}", fg="red", err=True)
            if ctx.obj.get("verbose", 0) > 0:
                raise
            sys.exit(1)

    if pptx_folder.name.endswith("_pptx"):
        process_folder(pptx_folder)
    else:
        folders = list(pptx_folder.glob("*_pptx"))

        if not folders:
            if not quiet:
                click.echo("No extracted folders (*_pptx) found in directory")
            return

        if not quiet:
            click.echo(f"Found {len(folders)} extracted folder(s)")

        for folder in folders:
            process_folder(folder)

        if not quiet:
            click.secho(f"\n✓ Processed {len(folders)} folder(s)", fg="green", bold=True)


if __name__ == "__main__":
    cli()
