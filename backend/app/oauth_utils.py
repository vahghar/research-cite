# app/oauth_utils.py

import requests

def push_citation_to_zotero(zotero_user_id: str, zotero_api_key: str, bibtex_str: str) -> bool:
    """
    Push a single BibTeX string as a Zotero item via the Zotero API.
    For simplicity, we create a “book” itemType. In reality, you'd parse fields
    (title, author, year) and build a JSON payload accordingly.
    """
    # Endpoint: https://api.zotero.org/users/{user_id}/items
    url = f"https://api.zotero.org/users/{zotero_user_id}/items"
    headers = {
        "Zotero-API-Key": zotero_api_key,
        "Content-Type": "application/json"
    }
    # Minimal payload (you may need to adjust itemType, etc.)
    data = [
        {
            "itemType": "journalArticle",
            "bibtex": bibtex_str,
            # Zotero can import from BibTeX string
        }
    ]
    resp = requests.post(url, json=data, headers=headers)
    return resp.status_code in (200, 201)
