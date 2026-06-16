#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
import zipfile
import argparse
import re
import unicodedata


SUPPORTED_EXTENSIONS = {".docx", ".pptx", ".pdf", ".html", ".htm"}


def safe_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("._-")
    return name or "document"


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def rewrite_image_links(md_file: Path, assets_dir: Path) -> None:
    if not md_file.exists():
        return

    content = md_file.read_text(encoding="utf-8")
    relative_assets = f"./{assets_dir.name}"

    def normalize_img_path(path: str) -> str:
        path = path.strip().strip('"').strip("'")
        parts = Path(path).parts

        if "media" in parts:
            idx = parts.index("media")
            tail = Path(*parts[idx:])
            return f"{relative_assets}/{tail.as_posix()}"

        image_name = Path(path).name
        return f"{relative_assets}/{image_name}"

    def replace_md_image(match):
        alt = match.group(1)
        path = match.group(2)
        new_path = normalize_img_path(path)
        return f"![{alt}]({new_path})"

    content = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        replace_md_image,
        content,
    )

    def replace_html_img(match):
        prefix = match.group(1)
        path = match.group(2)
        suffix = match.group(3)
        new_path = normalize_img_path(path)
        return f"{prefix}{new_path}{suffix}"

    content = re.sub(
        r'(<img[^>]+src=["\'])([^"\']+)(["\'][^>]*>)',
        replace_html_img,
        content,
        flags=re.IGNORECASE,
    )

    md_file.write_text(content, encoding="utf-8")


def convert_docx(file: Path, output_md: Path, assets_dir: Path) -> None:
    run_command([
        "pandoc",
        str(file),
        "-t", "gfm",
        "--extract-media", str(assets_dir),
        "-o", str(output_md),
    ])

    rewrite_image_links(output_md, assets_dir)


def convert_html(file: Path, output_md: Path, assets_dir: Path) -> None:
    run_command([
        "pandoc",
        str(file),
        "-t", "gfm",
        "--extract-media", str(assets_dir),
        "-o", str(output_md),
    ])

    rewrite_image_links(output_md, assets_dir)


def convert_pdf(file: Path, output_md: Path, assets_dir: Path) -> None:
    run_command([
        "docling",
        str(file),
        "--to", "md",
        "--image-export-mode", "referenced",
        "--output", str(file.parent),
    ])

    generated_md = file.with_suffix(".md")
    original_artifacts_dir = file.parent / f"{file.stem}_artifacts"

    if generated_md.exists() and generated_md != output_md:
        if output_md.exists():
            output_md.unlink()
        generated_md.rename(output_md)

    if original_artifacts_dir.exists():
        if assets_dir.exists():
            shutil.rmtree(assets_dir)
        original_artifacts_dir.rename(assets_dir)

    rewrite_image_links(output_md, assets_dir)


def extract_pptx_images(file: Path, assets_dir: Path) -> None:
    with zipfile.ZipFile(file, "r") as pptx:
        for item in pptx.namelist():
            if item.startswith("ppt/media/"):
                filename = Path(item).name
                if filename:
                    safe_filename = safe_name(filename)
                    target = assets_dir / safe_filename

                    with pptx.open(item) as source, open(target, "wb") as dest:
                        dest.write(source.read())


def convert_pptx(file: Path, output_md: Path, assets_dir: Path) -> None:
    with open(output_md, "w", encoding="utf-8") as md_file:
        subprocess.run(
            ["markitdown", str(file)],
            stdout=md_file,
            check=True,
        )

    extract_pptx_images(file, assets_dir)
    rewrite_image_links(output_md, assets_dir)


def convert_file(file: Path) -> None:
    ext = file.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return

    clean_base = safe_name(file.stem)

    output_md = file.parent / f"{clean_base}.md"
    assets_dir = file.parent / clean_base
    assets_dir.mkdir(exist_ok=True)

    print(f"Convirtiendo: {file}")
    print(f"Markdown:    {output_md}")
    print(f"Assets:      {assets_dir}")

    try:
        if ext == ".docx":
            convert_docx(file, output_md, assets_dir)

        elif ext in {".html", ".htm"}:
            convert_html(file, output_md, assets_dir)

        elif ext == ".pdf":
            convert_pdf(file, output_md, assets_dir)

        elif ext == ".pptx":
            convert_pptx(file, output_md, assets_dir)

        print(f"OK: {output_md}\n")

    except subprocess.CalledProcessError as e:
        print(f"ERROR convirtiendo {file}: {e}\n")


def validate_dependencies() -> None:
    required = ["pandoc", "docling", "markitdown"]
    missing = [cmd for cmd in required if not command_exists(cmd)]

    if missing:
        print("Faltan dependencias:")
        for cmd in missing:
            print(f"  - {cmd}")
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convierte DOCX, PDF, PPTX, HTML/HTM a Markdown."
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directorio raíz a recorrer.",
    )

    args = parser.parse_args()
    root = Path(args.directory).resolve()

    if not root.exists():
        raise SystemExit(f"El directorio no existe: {root}")

    validate_dependencies()

    files = [
        file for file in root.rglob("*")
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    print(f"Archivos encontrados: {len(files)}\n")

    for file in files:
        convert_file(file)

    print("Conversión finalizada.")


if __name__ == "__main__":
    main()
