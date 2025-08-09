import shutil
from pathlib import Path

import click

from dotpptx.dotpptx import dopptx_folder, unpptx_file


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def unpptx(path: Path) -> None:
    if path.is_file():
        unpptx_file(path.parent, path)
    else:
        for pptx_file in path.glob("*.pptx"):
            if pptx_file.stem.startswith("~$"):
                continue

            unpptx_file(path, pptx_file)

@cli.command()
@click.argument("pptx-folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--delete-original", is_flag=True, default=False)
def dopptx(pptx_folder: Path, delete_original: bool) -> None:
    if pptx_folder.name.endswith("_pptx"):
        dopptx_folder(pptx_folder.parent, pptx_folder)

        if delete_original:
            shutil.rmtree(pptx_folder)

    else:
        for pptx_exploded_folder in pptx_folder.glob("*_pptx"):
            dopptx_folder(pptx_folder, pptx_exploded_folder)

            if delete_original:
                shutil.rmtree(pptx_exploded_folder)

if __name__ == "__main__":
    cli()