import os
import arxiv
import requests
import fitz  # PyMuPDF
import re
import json
from typing import List, Tuple, Dict, Any


# Define domains and search terms
DOMAINS = {
    "Materials Science": "materials science",
    "Physics": "quantum physics",
    "Computer Science": "machine learning"
}


def split_into_chunks(text: str) -> List[Tuple[str, str]]:
    """
    Split the text into general and specialized chunks based on section headings.

    Args:
        text (str): Full text of the paper.

    Returns:
        List[Tuple[str, str]]: List of (chunk_type, chunk_text) tuples.
    """
    section_names = [
        "abstract", "introduction", "methods", "results", "discussion", "conclusion"
    ]
    pattern = r"(?i)^\s*(?:" + "|".join(section_names) + r")\s*:?\s*$"
    parts = re.split(pattern, text, flags=re.MULTILINE)

    if len(parts) <= 1:
        # If no sections are matched, treat the whole text as a general chunk
        return [("general", text.strip())] if text.strip() else []

    chunks = []
    for i in range(0, len(parts) - 1, 2):
        section_name = parts[i].strip().lower()
        section_text = parts[i + 1].strip()
        if section_name in ["abstract", "introduction", "conclusion"]:
            chunk_type = "general"
        elif section_name in ["methods", "results", "discussion"]:
            chunk_type = "specialized"
        else:
            continue
        if section_text:
            chunks.append((chunk_type, section_text))

    return chunks


def process_paper(filepath: str, domain: str) -> List[Dict[str, Any]]:
    """
    Process a single paper: extract text and chunk it.

    Args:
        filepath (str): Path to the PDF file.
        domain (str): Domain of the paper.

    Returns:
        List[Dict[str, Any]]: List of JSON entries for each chunk.
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        chunks = split_into_chunks(text)
        json_entries = []
        for chunk_type, chunk_content in chunks:
            entry = {
                "domain": domain,
                "chunk_type": chunk_type,
                "text": chunk_content
            }
            json_entries.append(entry)
        return json_entries
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def download_arxiv_papers(domain: str, search_query: str, max_results: int = 50):
    """
    Download papers from arXiv for a given domain.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    domain_dir = os.path.join("papers", domain, "arxiv")
    os.makedirs(domain_dir, exist_ok=True)

    for result in client.results(search):
        paper_id = result.entry_id.split("/")[-1]
        filepath = os.path.join(domain_dir, f"{paper_id}.pdf")
        if not os.path.exists(filepath):
            try:
                # Download using requests instead of result.download_pdf
                pdf_response = requests.get(result.pdf_url)
                if pdf_response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(pdf_response.content)
                    print(f"Downloaded {paper_id} to {filepath}")
                else:
                    print(f"Failed to download {paper_id}, status code: {pdf_response.status_code}")
            except Exception as e:
                print(f"Error downloading {paper_id}: {e}")


def download_chemrxiv_papers(domain: str, max_results: int = 50):
    """
    Download papers from ChemRxiv for Materials Science.
    """
    if domain != "Materials Science":
        return
    domain_dir = os.path.join("papers", domain, "chemrxiv")
    os.makedirs(domain_dir, exist_ok=True)

    url = "https://chemrxiv.org/engage/api/v1/items?limit=" + str(max_results)
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        for item in items:
            pdf_url = item.get("pdfUrl")
            if pdf_url:
                paper_id = item.get("id")
                filepath = os.path.join(domain_dir, f"{paper_id}.pdf")
                if not os.path.exists(filepath):
                    pdf_response = requests.get(pdf_url)
                    with open(filepath, "wb") as f:
                        f.write(pdf_response.content)
                    print(f"Downloaded ChemRxiv {paper_id} to {filepath}")


def main():
    """
    Main function to download and process papers.
    """
    for domain, search_query in DOMAINS.items():
        print(f"Processing domain: {domain}")

        # Download papers
        download_arxiv_papers(domain, search_query)
        download_chemrxiv_papers(domain)

        # Process papers and create corpus
        json_dir = os.path.join("papers", domain, "json")
        os.makedirs(json_dir, exist_ok=True)

        for source in ["arxiv", "chemrxiv"]:
            source_dir = os.path.join("papers", domain, source)
            if not os.path.exists(source_dir):
                continue
            for filename in os.listdir(source_dir):
                if filename.endswith(".pdf"):
                    filepath = os.path.join(source_dir, filename)
                    entries = process_paper(filepath, domain)
                    if entries:
                        json_filepath = os.path.join(json_dir, f"{filename[:-4]}.json")
                        with open(json_filepath, "w", encoding="utf-8") as f:
                            json.dump(entries, f, indent=2)
                        print(f"Saved JSON to {json_filepath}")


if __name__ == "__main__":
    main()
