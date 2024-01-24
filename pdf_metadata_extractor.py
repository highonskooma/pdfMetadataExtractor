import os
import json
from pypdf import PdfReader
from wand.image import Image

def load_processed_records(record_path):
    if os.path.exists(record_path):
        #print(f'Loading processed records from {record_path}...')
        with open(record_path, 'r') as record_file:
            return json.load(record_file)
    return {}

def save_processed_record(record_path, processed_files):
    with open(record_path, 'w') as record_file:
        json.dump(processed_files, record_file, indent=2)

def is_directory_processed(records, directory):
    for record in records:
        if 'directory' in record and record['directory'] == directory:
            return True
    return False

def mark_file_as_processed(record, file_path):
    record[file_path] = {'metadata': True, 'thumbnail': True}

def extract_metadata(pdf_path, noTitleCount):
    print(f'Processing {pdf_path}...')
    
    # Load processed records
    processed_records_path = os.getcwd() + '\\' + 'metadata.json'
    processed_records = load_processed_records(processed_records_path)

    # Extract directory from the file path
    file_directory = os.path.dirname(pdf_path)
    
    # Check if the file has already been processed
    if is_directory_processed(processed_records, file_directory):
        print(f'Skipping {pdf_path} - Already processed.')
        return {}, noTitleCount
    
    try:
        pdf_document = PdfReader(pdf_path)
        if pdf_document.metadata is None:
            print(f'No metadata found for {pdf_path}')
            return {}, noTitleCount
        title = pdf_document.metadata.title 
        if not title:
            noTitleCount += 1
            title = os.path.basename(pdf_path)
        metadata = {
            'title': title,
            'author': pdf_document.metadata.author,
            'subject': pdf_document.metadata.subject,
            'creator': pdf_document.metadata.creator,
            'producer': pdf_document.metadata.producer,
            'size': os.path.getsize(pdf_path),
            'directory': os.path.dirname(pdf_path),
            'thumbnail_path': generate_thumbnail(pdf_path)
        }
        return metadata, noTitleCount

    except Exception as e:
        print(f'Error processing {pdf_path}: {str(e)}')
        return {}, noTitleCount

    # Mark the file as processed
    mark_file_as_processed(processed_records, pdf_path)
    save_processed_record(processed_records_path, processed_records)
    
    return metadata, noTitleCount

def generate_thumbnail(pdf_path, page_number=0, thumbnail_size=(595, 842)):
    with Image(filename=f'{pdf_path}[{page_number}]', resolution=100) as img:
        img.convert("png")
        img.thumbnail(*thumbnail_size)

        parent_path = os.getcwd()
        images_folder = os.path.join(parent_path, 'images')
        os.makedirs(images_folder, exist_ok=True)

        thumbnail_path = os.path.join(images_folder, os.path.basename(pdf_path) + '_thumbnail.png')
        img.save(filename=thumbnail_path)
        return thumbnail_path

def process_folder(folder_path):
    metadata_list = []
    noTitleCount = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                metadata, noTitleCount = extract_metadata(file_path, noTitleCount)
                metadata_list.append(metadata)
    print(f'{noTitleCount} out of {len(metadata_list)} files had no title metadata.')
    return metadata_list

def save_to_json(metadata_list, output_json):
    with open(output_json, 'w') as json_file:
        json.dump(metadata_list, json_file, indent=2)

if __name__ == "__main__":
    current_directory = os.getcwd()
    output_json = 'metadata.json'

    metadata_list = process_folder(current_directory)
    save_to_json(metadata_list, output_json)
