from Bio import Entrez
import xml.etree.ElementTree as ET
import json
from typing import List, Dict
import os

Entrez.email = "ferinaderi@gmail.com"  

def fetch_clean_pubmed_abstracts(pmid: List[str]) -> List[Dict[str, str]]:
    results = []

    for pubmed_id in pmid:
        print(f"Searching: {pubmed_id}")
        try:
            # 1: fetch structured xml data
            fetch = Entrez.efetch(db="pubmed", id=pubmed_id, rettype="abstract", retmode="xml")
            xml_data = fetch.read()
            fetch.close()

            # 2: parse title and abstract text
            root = ET.fromstring(xml_data)
            title_elem = root.find(".//ArticleTitle")
            title = title_elem.text.strip() if title_elem is not None else "N/A"
            abstract_text = ""
            for elem in root.findall(".//AbstractText"):
                part = elem.text
                if part:
                    abstract_text += part.strip() + " "

            abstract_text = abstract_text.strip()
            print(f"found abstract (PMID: {pubmed_id})")

            results.append({
                "title": title,
                "pubmed_id": pubmed_id,
                "abstract": abstract_text
            })
        except Exception as e:
            print(f"Error processing '{pubmed_id}': {e}")
            continue

    return results

if __name__ == "__main__":
    pmid = [
        "15858239",
        "20598273",
        "6650562"
    ]

    abstracts = fetch_clean_pubmed_abstracts(pmid)
    destination_folder = "data/"
    os.makedirs(destination_folder, exist_ok=True)
    output_path = os.path.join(destination_folder, "abstracts.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(abstracts, f, indent=2, ensure_ascii=False)

    print(f"saved {len(abstracts)} abstracts to: {output_path}")
