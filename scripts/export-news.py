#!/usr/bin/env python3
"""Build a new static Pages artifact from approved BEBB_News posts only."""

import argparse
from datetime import date
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET


TEI = "{http://www.tei-c.org/ns/1.0}"
XML = "{http://www.w3.org/XML/1998/namespace}"
NS = {"t": TEI[1:-1]}
IMAGE_NAME = re.compile(r"[A-Za-z0-9._~-]+\.(?:png|jpe?g|gif|webp)", re.I)


def export_news(source, output):
    feed = ET.Element("bebb-news", version="1")
    ids = set()
    images = {}
    posts = source / "posts"
    if posts.is_symlink() or not posts.is_dir():
        raise ValueError("Expected a real posts/ directory")
    for path in sorted(posts.glob("*.xml")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported: {path}")
        xml = path.read_text(encoding="utf-8")
        if "<!DOCTYPE" in xml:
            raise ValueError(f"Unexpected DOCTYPE: {path}")
        post = ET.fromstring(xml)
        if post.tag != TEI + "TEI":
            raise ValueError(f"Expected a TEI document: {path}")
        news = post.find("t:text/t:body/t:div[@type='news']", NS)
        if news is None or news.get("subtype") != "published":
            continue

        date_node = post.find("t:teiHeader/t:fileDesc/t:publicationStmt/t:date", NS)
        when = date_node.get("when", "") if date_node is not None else ""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", when):
            raise ValueError(f"A published post needs a YYYY-MM-DD date: {path}")
        if date.fromisoformat(when) > date.today():
            continue
        post_id = post.get(XML + "id", "")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", post_id) or post_id in ids:
            raise ValueError(f"Missing, invalid, or duplicate xml:id: {path}")
        ids.add(post_id)

        # Export only the fields the website reads; editorial header notes stay in Git.
        public = ET.SubElement(feed, TEI + "TEI", {XML + "id": post_id})
        if post.get(XML + "lang"):
            public.set(XML + "lang", post.get(XML + "lang"))
        header = ET.SubElement(public, TEI + "teiHeader")
        file_desc = ET.SubElement(header, TEI + "fileDesc")
        title = post.find("t:teiHeader/t:fileDesc/t:titleStmt/t:title", NS)
        title_text = "".join(title.itertext()).strip() if title is not None else ""
        if not title_text:
            raise ValueError(f"A published post needs a title: {path}")
        ET.SubElement(ET.SubElement(file_desc, TEI + "titleStmt"), TEI + "title").text = title_text
        ET.SubElement(ET.SubElement(file_desc, TEI + "publicationStmt"), TEI + "date", when=when)
        term = post.find(
            "t:teiHeader/t:profileDesc/t:textClass/t:keywords[@scheme='#bebb-news']/"
            "t:term[@type='homepage']", NS
        )
        if term is not None:
            text_class = ET.SubElement(ET.SubElement(header, TEI + "profileDesc"), TEI + "textClass")
            keywords = ET.SubElement(text_class, TEI + "keywords", scheme="#bebb-news")
            ET.SubElement(keywords, TEI + "term", type="homepage").text = "".join(term.itertext())
        text = ET.SubElement(public, TEI + "text")
        language = post.find("t:text", NS).get(XML + "lang")
        if language:
            text.set(XML + "lang", language)
        ET.SubElement(text, TEI + "body").append(news)
        if any(node.get("type") == "internal" or node.get("subtype") == "internal" for node in news.iter()):
            raise ValueError(f"Remove internal material from the published text: {path}")
        graphic = news.find("t:figure/t:graphic[@url]", NS)
        if graphic is not None:
            name = graphic.get("url").strip()
            if not IMAGE_NAME.fullmatch(name):
                raise ValueError(f"Invalid image name in {path}")
            image = source / "images" / name
            if image.parent.is_symlink() or image.is_symlink() or not image.is_file():
                raise ValueError(f"Missing or unsafe image: {image}")
            images[name] = image

    ET.register_namespace("tei", NS["t"])
    xml = ET.tostring(feed, encoding="utf-8", xml_declaration=True)
    if len(xml) > 524288:
        raise ValueError("The feed exceeds the 512 KiB limit")
    output.mkdir(parents=True, exist_ok=False)
    (output / "feed.xml").write_bytes(xml)
    if images:
        (output / "images").mkdir()
        for name, image in images.items():
            shutil.copyfile(image, output / "images" / name)
    return len(ids)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="BEBB_News checkout")
    parser.add_argument("output", type=Path, help="new output directory")
    args = parser.parse_args()
    try:
        print(f"Exported {export_news(args.source, args.output)} approved posts.")
    except (ValueError, OSError, ET.ParseError) as error:
        parser.exit(1, f"News export: {error}\n")


if __name__ == "__main__":
    main()
