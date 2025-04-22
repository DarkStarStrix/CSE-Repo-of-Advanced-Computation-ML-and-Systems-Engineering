import os
import json
import glob
from typing import List, Dict, Any


def combine_json_files(directories: List [str], output_path: str) -> None:
    """
    Combines all JSON files from the given directories into a single large JSON file.

    Args:
        directories: List of directory paths containing JSON files
        output_path: Path where the combined JSON file will be saved
    """
    all_entries = []
    total_files = 0

    print (f"Starting to process JSON files from {len (directories)} directories...")

    for directory in directories:
        if not os.path.exists (directory):
            print (f"Warning: Directory {directory} does not exist, skipping.")
            continue

        # Get all JSON files in the directory
        json_files = glob.glob (os.path.join (directory, "*.json"))
        print (f"Found {len (json_files)} JSON files in {directory}")

        for json_file in json_files:
            try:
                with open (json_file, 'r', encoding='utf-8') as f:
                    data = json.load (f)

                # Check if the data is a list (as expected from your original script)
                if isinstance (data, list):
                    all_entries.extend (data)
                else:
                    # If it's a single object, add it directly
                    all_entries.append (data)

                total_files += 1

            except Exception as e:
                print (f"Error processing {json_file}: {e}")

    # Create the directory if it doesn't exist
    os.makedirs (os.path.dirname (output_path), exist_ok=True)

    # Write the combined data to the output file
    with open (output_path, 'w', encoding='utf-8') as f:
        json.dump (all_entries, f, indent=2)

    print (f"Successfully combined {total_files} JSON files into {output_path}")
    print (f"Total entries in the combined file: {len (all_entries)}")


if __name__ == "__main__":
    # Define directories and output path
    json_directories = [
        r"C:\Users\kunya\PyCharmMiscProject\Pre-Processing scripts\papers\Computer Science\json",
        r"C:\Users\kunya\PyCharmMiscProject\Pre-Processing scripts\papers\Materials Science\json",
        r"C:\Users\kunya\PyCharmMiscProject\Pre-Processing scripts\papers\Physics\json"
    ]

    output_file = r"C:\Users\kunya\PyCharmMiscProject\Pre-Processing scripts\papers\combined_scientific_papers.json"

    # Execute the combining process
    combine_json_files (json_directories, output_file)
