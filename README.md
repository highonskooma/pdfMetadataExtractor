# pdfMetadataExtractor

 A python script that recursively extracts pdf metadata from any pdf in a subfolder.\
 It also extracts thumbnails from each file and stores them in an images folder

## Requirements

- Download and install [Ghostcript](https://www.ghostscript.com/releases/index.html)\
This will extract the pdf metadata
- Download and install [ImageMagick](https://imagemagick.org/script/download.php)\
This will create the pdf thumbnails

## Setup

Run `pip install` to install project dependencies (pypdf, wand, argparse).

or if you're on Arch there are AUR packages for each one of these.

## Usage

- `-d` or `--directory` will specify the directory to be scanned

Example: `python .\pdf_metadata_extractor.py -d pdf_folder`
