import os
import json
from pathlib import Path
from pypdf import PdfReader
from wand.image import Image
import argparse

def load_processed_records(record_path):
    if os.path.exists(record_path):
        with open(record_path, 'r') as record_file:
            return json.load(record_file)
    return {}

def is_path_processed(records, filefolder, filename):
    if filefolder in records.keys():
        # extract the list of titles from records[filefolder]
        titles = [record['file_name'] for record in records[filefolder]]
        if filename in titles:
            return True
        else:
            return False        
    return False

def extract_metadata(pdf_path, parent_path, noTitleCount):
    # print(f'Processing {pdf_path}...')
        
    try:
        pdf_document = PdfReader(pdf_path)
        if pdf_document.metadata is None:
            # print(f'No metadata found for {pdf_path}')
            return {}, noTitleCount
        title = pdf_document.metadata.title 
        if not title:
            noTitleCount += 1
            title = os.path.basename(pdf_path)
        metadata = {
            'title': title,
            'file_name': os.path.splitext(os.path.basename(pdf_path))[0],
            'author': pdf_document.metadata.author,
            'subject': pdf_document.metadata.subject,
            'creator': pdf_document.metadata.creator,
            'producer': pdf_document.metadata.producer,
            'size': os.path.getsize(pdf_path),
            'thumbnail_path': generate_thumbnail(pdf_path, parent_path)
        }
        return metadata, noTitleCount

    except Exception as e:
        # print(f'Error processing {pdf_path}: {str(e)}')
        return {}, noTitleCount
    
def generate_thumbnail(pdf_path, parent_path, page_number=0, thumbnail_size=(595, 842)):
    with Image(filename=f'{pdf_path}[{page_number}]', resolution=100) as img:
        img.convert("png")
        img.thumbnail(*thumbnail_size)

        images_folder = os.path.join(parent_path, 'images')
        os.makedirs(images_folder, exist_ok=True)

        pdf_without_extension = Path(os.path.basename(pdf_path)).stem
        thumbnail_path = os.path.join(images_folder, pdf_without_extension + '_thumbnail.png')
        img.save(filename=thumbnail_path)
        return pdf_without_extension + '_thumbnail.png'
    
def load_metadata_list(processed_records):
    metadata_list = processed_records

    return metadata_list

def process_folder(folder_path):
    # Load processed records
    processed_records_path = folder_path + '\\' + 'metadata.json'
    processed_records = load_processed_records(processed_records_path)

    metadata_list = load_metadata_list(processed_records)
    noTitleCount = 0
    for root, dirs, files in os.walk(folder_path):
        dirName = os.path.basename(root)
        print('Scanning for files in', dirName)
        if not files:
            metadata_list[dirName] = []
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                file_folder = root
                
                # Check if the file has already been processed
                if is_path_processed(processed_records, file_folder, file):
                    # print(f'Skipping {file_path} - Already processed.')
                    continue
                
                metadata, noTitleCount = extract_metadata(file_path, folder_path, noTitleCount)

                # chcek if metadata_values disctionary has a file_path key, if so, update the metadata_list, else add a new entry                
                if dirName in metadata_list.keys():
                    metadata_list[dirName].append(metadata)
                else:
                    metadata_list[dirName] = [metadata]

    # print(f'{noTitleCount} out of {len(metadata_list)} files had no title metadata.')
    return metadata_list

def save_to_json(metadata_list, output_json):
    with open(output_json, 'w') as json_file:
        json.dump(metadata_list, json_file, indent=2)

def main():
    parser = argparse.ArgumentParser(description='PDF Metadata Extraction Script')
    parser.add_argument('-d', '--directory', help='Directory to scan for PDF files')
    args = parser.parse_args()

    if args.directory:
        folder_path = args.directory
    else:
        folder_path = os.getcwd()

    output_json = 'metadata.json'

    metadata_list = process_folder(folder_path)
    save_to_json(metadata_list, output_json)

if __name__ == "__main__":
    main()
