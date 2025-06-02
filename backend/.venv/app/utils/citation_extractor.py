# app/utils/citation_extractor.py

import re
import json
import bibtexparser
from groq import Groq
from ..core.config import settings

client = Groq(api_key='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')

def extract_reference_section(full_text: str) -> str:
    """
    Very naïve: look for "References" or "Bibliography" heading and return text after it.
    You can refine with better regex or PyMuPDF metadata sections.
    """
    patterns = [r"\nReferences\n", r"\nREFERENCES\n", r"\nBibliography\n"]
    for pat in patterns:
        split_res = re.split(pat, full_text, flags=re.IGNORECASE)
        if len(split_res) >= 2:
            return split_res[1]
    return ""

def extract_citations_from_references(ref_text: str) -> list[str]:
    """
    Ask the LLM: "Given the reference section, return a JSON list where each entry is
    a BibTeX string (or APA) of every citation in the references. If a reference lacks
    BibTeX, convert it to a minimal BibTeX. Return only the list."
    """
    prompt = f"""
    You are an expert at converting reference lists into BibTeX entries. 
    Given the following raw reference section, return a JSON array of strings. 
    Each string MUST be a complete BibTeX entry. Do not include any other text 
    or explanation—only the JSON array of BibTeX entries.

    Reference Section:
    \"\"\"
    {ref_text}
    \"\"\"
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You convert reference lists to BibTeX."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            # The response should be a JSON object containing the array
            response_json = json.loads(content)
            if isinstance(response_json, dict):
                # Look for the array in the response (might be nested)
                for value in response_json.values():
                    if isinstance(value, list):
                        return value
            return []
        except json.JSONDecodeError:
            return []
            
    except Exception as e:
        print(f"Error extracting citations with Groq: {e}")
        return []

def bibtex_to_fields(bibtex_str: str) -> dict:
    """
    Parse BibTeX string into a dictionary of fields.
    Uses bibtexparser library for reliable parsing.
    """
    try:
        bib_db = bibtexparser.loads(bibtex_str)
        if bib_db.entries:
            entry = bib_db.entries[0]
            return entry
    except Exception as e:
        print(f"Error parsing BibTeX: {e}")
    return {}