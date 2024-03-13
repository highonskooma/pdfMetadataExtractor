import os
import argparse
import json

def scan_dir(parent_dir, result):
    entries = os.listdir(parent_dir)
    subdirectories = [entry for entry in entries if os.path.isdir(os.path.join(parent_dir, entry))]
    result[os.path.basename(parent_dir)] = subdirectories
    for subdir in subdirectories:
        scan_dir(os.path.join(parent_dir, subdir), result)

def save_to_json(dir_structure, output_json):
    with open(output_json, 'w') as json_file:
        json.dump(dir_structure, json_file, indent=2)

def main():
    parser = argparse.ArgumentParser(description='PDF Metadata Extraction Script')
    parser.add_argument('-d', '--directory', help='Directory to scan for PDF files')
    args = parser.parse_args()

    if args.directory:
        dir = args.directory
    else:
        dir = os.getcwd()

    output_json = 'dir_structure.json'
    
    result = {}
    scan_dir(dir, result)
    save_to_json(result, output_json)

    print(result)
    print("\n 󰄲 Scan complete. ",len(result)," directories scanned.")

if __name__ == "__main__":
    main()
