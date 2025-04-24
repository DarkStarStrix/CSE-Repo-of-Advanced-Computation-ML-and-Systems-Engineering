#!/usr/bin/env python3
"""
CSE++ Journal Paper Validation Script
-------------------------------------
This script validates a paper submission according to the
CSE++ Journal standards and requirements.
"""

import os
import sys
import json
import argparse
import glob
from pathlib import Path


class PaperValidator:
    def __init__(self, paper_dir):
        self.paper_dir = Path (paper_dir)
        self.errors = []
        self.warnings = []

    def validate(self):
        """Run all validation checks and return success status"""
        if not self.paper_dir.exists ():
            self.errors.append (f"Paper directory '{self.paper_dir}' does not exist")
            return False

        self._check_required_files ()
        self._validate_metadata ()
        self._check_citation ()
        self._check_code_directory ()
        self._check_figures_directory ()

        if self.errors:
            print ("\n❌ VALIDATION FAILED")
            for error in self.errors:
                print (f"ERROR: {error}")
        else:
            print ("\n✅ VALIDATION PASSED")

        if self.warnings:
            print ("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print (f"WARNING: {warning}")

        return len (self.errors) == 0

    def _check_required_files(self):
        """Check if all required files exist"""
        # Check for metadata.json
        if not (self.paper_dir / "metadata.json").exists ():
            self.errors.append ("Missing metadata.json")

        # Check for CITATION.bib
        if not (self.paper_dir / "CITATION.bib").exists ():
            self.errors.append ("Missing CITATION.bib")

        # Check for PDF file
        pdf_files = list (self.paper_dir.glob ("*.pdf"))
        if not pdf_files:
            self.errors.append ("No PDF file found")
        elif len (pdf_files) > 1:
            self.warnings.append (f"Multiple PDF files found: {', '.join (f.name for f in pdf_files)}")

        # Check for README.md
        if not (self.paper_dir / "README.md").exists ():
            self.warnings.append ("Missing README.md")

    def _validate_metadata(self):
        """Validate the metadata.json file"""
        metadata_path = self.paper_dir / "metadata.json"
        if not metadata_path.exists ():
            return

        try:
            with open (metadata_path, 'r') as f:
                metadata = json.load (f)

            # Check required fields
            required_fields = ['title', 'author', 'date', 'abstract', 'keywords']
            for field in required_fields:
                if field not in metadata:
                    self.errors.append (f"Missing required field '{field}' in metadata.json")
                elif not metadata [field]:
                    self.errors.append (f"Empty required field '{field}' in metadata.json")

            # Check keywords
            if 'keywords' in metadata and isinstance (metadata ['keywords'], list):
                if len (metadata ['keywords']) < 3:
                    self.warnings.append (f"Less than 3 keywords provided ({len (metadata ['keywords'])})")

        except json.JSONDecodeError:
            self.errors.append ("Invalid JSON format in metadata.json")
        except Exception as e:
            self.errors.append (f"Error processing metadata.json: {str (e)}")

    def _check_citation(self):
        """Check the CITATION.bib file"""
        citation_path = self.paper_dir / "CITATION.bib"
        if not citation_path.exists ():
            return

        try:
            with open (citation_path, 'r') as f:
                content = f.read ()

            # Basic BibTeX format validation
            if not content.strip ().startswith ('@'):
                self.errors.append ("CITATION.bib does not appear to be a valid BibTeX entry")

            # Check for placeholder text
            placeholders = ["Paper Title Here", "Your Name"]
            for placeholder in placeholders:
                if placeholder in content:
                    self.errors.append (f"CITATION.bib contains placeholder text: '{placeholder}'")

        except Exception as e:
            self.errors.append (f"Error processing CITATION.bib: {str (e)}")

    def _check_code_directory(self):
        """Check the code directory"""
        code_dir = self.paper_dir / "code"
        if not code_dir.exists ():
            self.warnings.append ("No code directory found")
            return

        # Check if there are any files in the code directory
        code_files = list (code_dir.glob ("*"))
        if not code_files:
            self.warnings.append ("Code directory is empty")

    def _check_figures_directory(self):
        """Check the figures directory"""
        figures_dir = self.paper_dir / "figures"
        if not figures_dir.exists ():
            self.warnings.append ("No figures directory found")
            return

        # Check if there are any image files in the figures directory
        figure_files = list (figures_dir.glob ("*.png")) + list (figures_dir.glob ("*.jpg")) + list (
            figures_dir.glob ("*.svg"))
        if not figure_files:
            self.warnings.append ("No figure files found (supported formats: PNG, JPG, SVG)")


def main():
    parser = argparse.ArgumentParser (description="Validate CSE++ Journal paper submission")
    parser.add_argument ("paper_dir", help="Path to the paper directory")
    args = parser.parse_args ()

    validator = PaperValidator (args.paper_dir)
    success = validator.validate ()

    sys.exit (0 if success else 1)


if __name__ == "__main__":
    main ()
