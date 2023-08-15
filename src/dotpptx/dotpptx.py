import xml.dom.minidom
import zipfile
from pathlib import Path


def unpptx_file(pptx_folder, pptx_file):
    output_folder = Path(pptx_folder) / f"{pptx_file.stem}_pptx"

    with zipfile.ZipFile(pptx_file, "r") as zip_ref:
        zip_ref.extractall(output_folder)

    def prettify_files(pattern):
        for xml_file in output_folder.glob(pattern):
            with open(xml_file, "r") as f:
                xml_string = f.read()
                dom = xml.dom.minidom.parseString(xml_string)
                pretty_xml_as_string = dom.toprettyxml()
            with open(xml_file, "w") as f:
                f.write(pretty_xml_as_string)

    prettify_files("**/*.xml")
    prettify_files("**/*.rels")


def dopptx_folder(pptx_folder, pptx_exploded_folder):
    deck_name = pptx_exploded_folder.stem[:-5]
    pptx_file = Path(pptx_folder) / f"{deck_name}.pptx"

    with zipfile.ZipFile(pptx_file, "w") as zip_ref:
        for file in pptx_exploded_folder.glob("**/*"):
            zip_ref.write(file, file.relative_to(pptx_exploded_folder))