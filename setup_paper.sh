#!/bin/bash
# Script to set up a new paper structure in the CSE++ Journal

# Check if a paper name was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 paper_name_year"
    echo "Example: $0 quantum_ml_2025"
    exit 1
fi

PAPER_NAME=$1
PAPER_DIR="PAPERS/$PAPER_NAME"

# Create the directory structure
mkdir -p "$PAPER_DIR/code"
mkdir -p "$PAPER_DIR/figures"

# Create placeholder metadata.json
cat > "$PAPER_DIR/metadata.json" << EOF
{
  "title": "Paper Title Here",
  "author": "Your Name",
  "date": "$(date +%Y-%m-%d)",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "journal": "CSE++ Journal of Advanced Computation, ML, and Systems Engineering",
  "version": "v1.0.0",
  "abstract": "Abstract goes here",
  "github_url": "https://github.com/lambda-ark/csepp-journal/tree/main/PAPERS/$PAPER_NAME"
}
EOF

# Create placeholder CITATION.bib
cat > "$PAPER_DIR/CITATION.bib" << EOF
@article{author$(date +%Y)title,
  title = {Paper Title Here},
  author = {Your Name},
  journal = {CSE++ Journal of Advanced Computation, ML, and Systems Engineering},
  year = {$(date +%Y)},
  month = {$(date +%B)},
  note = {Version 1.0.0},
  url = {https://github.com/lambda-ark/csepp-journal/tree/main/PAPERS/$PAPER_NAME}
}
EOF

# Create a README for the paper
cat > "$PAPER_DIR/README.md" << EOF
# Paper Title Here

## Abstract

Abstract goes here

## Code

The \`code/\` directory contains all scripts needed to reproduce the results in this paper.

## Figures

The \`figures/\` directory contains all figures used in the paper.

## Citation

Please use the provided CITATION.bib file when referencing this work.
EOF

echo "Created paper structure at $PAPER_DIR"
echo "Don't forget to:"
echo "1. Add your paper.pdf"
echo "2. Update metadata.json with correct information"
echo "3. Update CITATION.bib with correct information"
echo "4. Add your code and figures"