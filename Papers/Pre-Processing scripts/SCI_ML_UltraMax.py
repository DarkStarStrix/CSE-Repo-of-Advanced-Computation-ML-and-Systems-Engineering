import os
import arxiv
import requests
import fitz  # PyMuPDF
import json
from typing import List, Dict, Any
import concurrent.futures
import threading

DOMAINS = {
    "Materials Science": "materials science",
    "Physics": "physics",
    "Biology": "biology"
}

lock = threading.Lock()

def download_arxiv_paper(result, domain_dir):
    """
    Download a single arXiv paper.
    """
    paper_id = result.entry_id.split("/")[-1]
    filepath = os.path.join(domain_dir, f"{paper_id}.pdf")
    if not os.path.exists(filepath):
        try:
            pdf_response = requests.get(result.pdf_url)
            if pdf_response.status_code == 200:
                with lock:
                    with open(filepath, "wb") as f:
                        f.write(pdf_response.content)
                print(f"Downloaded {paper_id} to {filepath}")
            else:
                print(f"Failed to download {paper_id}, status code: {pdf_response.status_code}")
        except Exception as e:
            print(f"Error downloading {paper_id}: {e}")

def download_arxiv_papers(domain: str, search_query: str, max_results: int = 50):
    """
    Download papers from arXiv for a given domain using multithreading.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    domain_dir = os.path.join("papers", domain, "arxiv")
    os.makedirs(domain_dir, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_arxiv_paper, result, domain_dir) for result in client.results(search)]
        concurrent.futures.wait(futures)

def download_chemrxiv_papers(domain: str, max_results: int = 50):
    """
    Download papers from ChemRxiv for Materials Science using multithreading.
    """
    if domain != "Materials Science":
        return
    domain_dir = os.path.join("papers", domain, "chemrxiv")
    os.makedirs(domain_dir, exist_ok=True)

    url = f"https://chemrxiv.org/engage/api/v1/items?limit={max_results}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for item in items:
                pdf_url = item.get("pdfUrl")
                if pdf_url:
                    paper_id = item.get("id")
                    filepath = os.path.join(domain_dir, f"{paper_id}.pdf")
                    if not os.path.exists(filepath):
                        futures.append(executor.submit(download_chemrxiv_paper, pdf_url, filepath, paper_id))
            concurrent.futures.wait(futures)
    else:
        print(f"Failed to retrieve ChemRxiv items, status code: {response.status_code}")

def download_chemrxiv_paper(pdf_url: str, filepath: str, paper_id: str):
    """
    Download a single ChemRxiv paper.
    """
    try:
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            with lock:
                with open(filepath, "wb") as f:
                    f.write(pdf_response.content)
            print(f"Downloaded ChemRxiv {paper_id} to {filepath}")
        else:
            print(f"Failed to download ChemRxiv {paper_id}, status code: {pdf_response.status_code}")
    except Exception as e:
        print(f"Error downloading ChemRxiv {paper_id}: {e}")

def process_paper(filepath: str, domain: str) -> Dict[str, Any]:
    """
    Process a single paper: extract full text and save as JSON.
    
    Args:
        filepath (str): Path to the PDF file.
        domain (str): Domain of the paper.
    
    Returns:
        Dict[str, Any]: JSON entry for the full paper text.
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        entry = {
            "domain": domain,
            "text": text.strip()
        }
        return entry
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return {}

def main():
    """
    Main function to download and process papers for the Ultramax dataset.
    """
    for domain, search_query in DOMAINS.items():
        print(f"Processing domain: {domain}")

        download_arxiv_papers(domain, search_query)
        if domain == "Materials Science":
            download_chemrxiv_papers(domain)

        json_dir = os.path.join("papers", domain, "json")
        os.makedirs(json_dir, exist_ok=True)

        for source in ["arxiv", "chemrxiv"]:
            source_dir = os.path.join("papers", domain, source)
            if not os.path.exists(source_dir):
                continue
            for filename in os.listdir(source_dir):
                if filename.endswith(".pdf"):
                    filepath = os.path.join(source_dir, filename)
                    entry = process_paper(filepath, domain)
                    if entry:
                        json_filepath = os.path.join(json_dir, f"{filename[:-4]}.json")
                        with lock:
                            with open(json_filepath, "w", encoding="utf-8") as f:
                                json.dump(entry, f, indent=2)
                        print(f"Saved JSON to {json_filepath}")

if __name__ == "__main__":
    main()
