#!/usr/bin/env python3
"""
CSE++ Journal Index Updater
---------------------------
This script updates the paper index and monthly snapshots
based on the papers in the PAPERS directory.
"""

import os
import sys
import json
import datetime
from pathlib import Path


class IndexUpdater:
    def __init__(self, repo_root):
        self.repo_root = Path (repo_root)
        self.papers_dir = self.repo_root / "PAPERS"
        self.index_file = self.repo_root / "paper_index.json"
        self.index_data = self._load_index ()

    def _load_index(self):
        """Load the existing index or create a new one"""
        if self.index_file.exists ():
            try:
                with open (self.index_file, 'r') as f:
                    return json.load (f)
            except json.JSONDecodeError:
                print (f"Error: Invalid JSON format in {self.index_file}")
                return self._create_empty_index ()
        else:
            return self._create_empty_index ()

    def _create_empty_index(self):
        """Create a new empty index structure"""
        return {
            "papers": [],
            "monthly_snapshots": {},
            "featured": [],
            "last_updated": datetime.datetime.now ().strftime ("%Y-%m-%d")
        }

    def update(self):
        """Update the index with all papers in the PAPERS directory"""
        if not self.papers_dir.exists ():
            print (f"Error: PAPERS directory not found at {self.papers_dir}")
            return False

        # Get all paper directories
        paper_dirs = [d for d in self.papers_dir.iterdir () if d.is_dir () and d.name != ".git"]

        # Process each paper directory
        existing_ids = [paper ["id"] for paper in self.index_data ["papers"]]
        papers_updated = 0

        for paper_dir in paper_dirs:
            paper_id = paper_dir.name
            metadata_file = paper_dir / "metadata.json"

            # Skip directories without metadata.json
            if not metadata_file.exists ():
                print (f"Warning: No metadata.json found in {paper_dir}")
                continue

            try:
                with open (metadata_file, 'r') as f:
                    metadata = json.load (f)

                # Create or update paper entry
                if paper_id in existing_ids:
                    # Update existing paper
                    for i, paper in enumerate (self.index_data ["papers"]):
                        if paper ["id"] == paper_id:
                            self.index_data ["papers"] [i] = self._create_paper_entry (paper_id, metadata)
                            papers_updated += 1
                else:
                    # Add new paper
                    self.index_data ["papers"].append (self._create_paper_entry (paper_id, metadata))
                    papers_updated += 1

                    # Add to current month's snapshot
                    current_month = datetime.datetime.now ().strftime ("%Y-%m")
                    if current_month not in self.index_data ["monthly_snapshots"]:
                        self.index_data ["monthly_snapshots"] [current_month] = []

                    if paper_id not in self.index_data ["monthly_snapshots"] [current_month]:
                        self.index_data ["monthly_snapshots"] [current_month].append (paper_id)

            except json.JSONDecodeError:
                print (f"Error: Invalid JSON format in {metadata_file}")
            except Exception as e:
                print (f"Error processing {paper_dir}: {str (e)}")

        # Update last_updated timestamp
        self.index_data ["last_updated"] = datetime.datetime.now ().strftime ("%Y-%m-%d")

        # Save the updated index
        with open (self.index_file, 'w') as f:
            json.dump (self.index_data, f, indent=2)

        print (f"Updated index with {papers_updated} papers")
        print (f"Total papers in index: {len (self.index_data ['papers'])}")

        return True

    def _create_paper_entry(self, paper_id, metadata):
        """Create a paper entry from metadata"""
        return {
            "id": paper_id,
            "title": metadata.get ("title", "Untitled"),
            "author": metadata.get ("author", "Unknown"),
            "date": metadata.get ("date", datetime.datetime.now ().strftime ("%Y-%m-%d")),
            "abstract": metadata.get ("abstract", ""),
            "keywords": metadata.get ("keywords", []),
            "doi": metadata.get ("doi", ""),
            "url": metadata.get ("github_url",
                                 f"https://github.com/lambda-ark/csepp-journal/tree/main/PAPERS/{paper_id}")
        }

    def add_to_featured(self, paper_id):
        """Add a paper to the featured list"""
        if paper_id not in self.index_data ["featured"]:
            self.index_data ["featured"].append (paper_id)
            print (f"Added {paper_id} to featured papers")
        else:
            print (f"{paper_id} is already in featured papers")

        # Save the updated index
        with open (self.index_file, 'w') as f:
            json.dump (self.index_data, f, indent=2)


def main():
    import argparse

    parser = argparse.ArgumentParser (description="Update CSE++ Journal paper index")
    parser.add_argument ("--repo-root", default=".", help="Path to the repository root")
    parser.add_argument ("--feature", help="Add paper ID to featured list")
    args = parser.parse_args ()

    updater = IndexUpdater (args.repo_root)

    if args.feature:
        updater.add_to_featured (args.feature)
    else:
        success = updater.update ()
        if not success:
            sys.exit (1)


if __name__ == "__main__":
    main ()
