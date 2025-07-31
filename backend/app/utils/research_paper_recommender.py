import requests
import re
from typing import List, Dict

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def extract_keywords(text: str, max_keywords: int = 8) -> List[str]:
    """
    Naive keyword extraction: extract unique, significant words (longer than 4 chars, not stopwords).
    """
    stopwords = set([
        'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
        'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
        'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
        'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
        'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just',
        'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once',
        'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she',
        'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves',
        'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until',
        'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
        'why', 'with', 'would',
    ])
    words = re.findall(r"\b\w{5,}\b", text.lower())
    keywords = [w for w in words if w not in stopwords]
    # Return most common keywords
    freq = {}
    for w in keywords:
        freq[w] = freq.get(w, 0) + 1
    sorted_keywords = sorted(freq, key=freq.get, reverse=True)
    return sorted_keywords[:max_keywords]


def recommend_papers(text: str, max_results: int = 5) -> List[Dict]:
    """
    Given a text, extract keywords and query Semantic Scholar for relevant papers.
    Returns a list of dicts with title, authors, abstract, url.
    """
    keywords = extract_keywords(text)
    if not keywords:
        return []
    query = " ".join(keywords)
    params = {
        "query": query,
        "fields": "title,authors,abstract,url,year",
        "limit": max_results,
    }
    try:
        resp = requests.get(SEMANTIC_SCHOLAR_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for paper in data.get("data", []):
            results.append({
                "title": paper.get("title"),
                "authors": ", ".join([a.get("name", "") for a in paper.get("authors", [])]),
                "abstract": paper.get("abstract", ""),
                "url": paper.get("url"),
                "year": paper.get("year"),
            })
        return results
    except Exception as e:
        print(f"Error querying Semantic Scholar: {e}")
        return [] 