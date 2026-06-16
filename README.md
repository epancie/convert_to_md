Document to Markdown Converter

A Python utility that recursively converts documents into Markdown while preserving images in a dedicated folder for each document.

Supported formats:

* Microsoft Word (.docx)
* Microsoft PowerPoint (.pptx)
* PDF (.pdf)
* HTML (.html, .htm)

The generated Markdown references images using relative paths, making the output portable and suitable for Git repositories, documentation sites, or RAG (Retrieval-Augmented Generation) pipelines.

⸻

Features

* Recursively scans a directory tree.
* Converts multiple document formats to Markdown.
* Creates one image directory per document.
* Generates relative image references.
* Sanitizes filenames and directories by replacing spaces and special characters.
* Preserves document hierarchy.
* Prevents image name collisions between documents.

Example:

```
docs/
├── Architecture Guide.docx
├── Architecture_Guide.md
├── Architecture_Guide/
│   └── media/
│       ├── image1.png
│       └── image2.png
│
├── Network Overview.pdf
├── Network_Overview.md
└── Network_Overview/
    ├── image1.png
    └── image2.png
```

⸻

Requirements

* Python 3.10 or newer
* Pandoc
* Docling
* MarkItDown

⸻

Installation

1. Clone the repository

```
git clone https://github.com/<your-user>/<repository>.git
cd <repository>
```
⸻

2. Install Pandoc

macOS
```
brew install pandoc
```
Ubuntu
```
sudo apt install pandoc
```
⸻

3. Install Python

Using uv (recommended):
```
uv python install 3.11
```
⸻

4. Create a virtual environment
```
uv venv --python 3.11
```
Activate it:

macOS / Linux
```
source .venv/bin/activate
```
Windows
```
.venv\Scripts\activate
```
⸻

5. Install dependencies
```
uv pip install docling markitdown
```
or
```
uv pip install -r requirements.txt
```
⸻

Usage

Convert every supported document under a directory:
```
python convert_to_md.py ./docs
```
If no directory is specified, the current directory is used:
```
python convert_to_md.py
```
⸻

Output

For each document, the script creates:

* One Markdown file
* One directory containing all extracted images

Example:

Input:

Architecture Guide.docx

Output:

Architecture_Guide.md
Architecture_Guide/
    media/
        image1.png
        image2.png

The Markdown will contain relative image references such as:
```
![](./Architecture_Guide/media/image1.png)
```
or
```
<img src="./Architecture_Guide/media/image2.png">
```
⸻

Filename normalization

To ensure portability across operating systems and Git repositories, filenames and image directories are normalized.

For example:

```
2026 Trends to Watch: Telco AI Software (Final).pdf
```
becomes
```
2026_Trends_to_Watch_Telco_AI_Software_Final.md
2026_Trends_to_Watch_Telco_AI_Software_Final/
```
This avoids issues caused by:

* spaces
* accented characters
* parentheses
* punctuation
* special symbols

⸻

Supported converters

Format	Converter
DOCX	Pandoc
PPTX	MarkItDown
PDF	Docling
HTML	Pandoc

⸻

Notes

* DOCX images are extracted using Pandoc.
* PPTX images are extracted directly from the PowerPoint package.
* PDF conversion uses Docling with referenced image export.
* Image references are automatically rewritten to use relative paths.

⸻

Limitations

* Complex SmartArt objects in PowerPoint may not be perfectly represented.
* OCR quality for scanned PDFs depends on Docling capabilities.
* Embedded multimedia (videos, audio) is not extracted.


