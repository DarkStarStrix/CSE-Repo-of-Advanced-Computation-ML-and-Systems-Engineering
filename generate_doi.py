#!/usr/bin/env python3
"""
CSE++ Journal DOI Generator Script
----------------------------------
This script generates a DOI-like identifier for papers in the journal.
While not official DOIs, these serve as persistent identifiers.
"""

import os
import sys
import json
import argparse
import hashlib
import datetime
from pathlib import Path


def generate_doi(paper_dir):
    """Generate a DOI-like identifier for a paper"""
    paper_dir = Path (paper_dir)

    # Check if paper directory exists
    if not paper_dir.exists ():
        print (f"Error: Paper directory '{paper_dir}' does not exist")
        return None

    # Load metadata
    metadata_path = paper_dir / "metadata.json"
    if not metadata_path.exists ():
        print (f"Error: metadata.json not found in {paper_dir}")
        return None

    try:
        with open (metadata_path, 'r') as f:
            metadata = json.load (f)
    except json.JSONDecodeError:
        print (f"Error: Invalid JSON format in {metadata_path}")
        return None
    except Exception as e:
        print (f"Error reading metadata.json: {str (e)}")
        return None

    # Extract required fields
    title = metadata.get ('title', '')
    author = metadata.get ('author', '')
    date = metadata.get ('date', '')

    if not title or not author or not date:
        print ("Error: Missing required metadata fields (title, author, date)")
        return None

    # Generate a hash based on title, author, and folder name
    hash_input = f"{title}:{author}:{paper_dir.name}"
    hash_value = hashlib.sha256 (hash_input.encode ()).hexdigest () [:8]

    # Format: csepp.YYYY.shortcode
    year = date.split ('-') [0] if '-' in date else datetime.datetime.now ().year
    doi = f"csepp.{year}.{hash_value}"

    # Update metadata with the DOI
    metadata ['doi'] = doi
    with open (metadata_path, 'w') as f:
        json.dump (metadata, f, indent=2)

    print (f"Generated DOI: {doi}")
    print (f"Updated metadata.json with DOI")

    return doi


def main():
    parser = argparse.ArgumentParser (description="Generate DOI for CSE++ Journal paper")
    parser.add_argument ("paper_dir", help="Path to the paper directory")
    args = parser.parse_args ()

    doi = generate_doi (args.paper_dir)
    if doi is None:
        sys.exit (1)

    print (f"\nDOI successfully generated: {doi}")
    print (f"Paper can now be cited using this identifier")


if __name__ == "__main__":
    main ()
