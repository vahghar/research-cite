# app/utils/citation_extractor.py

import re
import os
import json
import bibtexparser
from groq import Groq
from ..core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def extract_reference_section(full_text: str) -> str:
    """
    Enhanced reference section extraction that handles various academic paper formats.
    Looks for multiple patterns and uses heuristics to find the most likely reference section.
    """
    # Common patterns for reference sections
    patterns = [
        r"\n\s*(References?|Bibliography|Literature Cited|Works Cited|Sources?)\s*\n",
        r"\n\s*(REFERENCES?|BIBLIOGRAPHY|LITERATURE CITED|WORKS CITED|SOURCES?)\s*\n",
        r"\n\s*(\d+\.\s*)?(References?|Bibliography|Literature Cited|Works Cited|Sources?)\s*\n",
        r"\n\s*(References?|Bibliography|Literature Cited|Works Cited|Sources?)\s*$",
        r"^\s*(References?|Bibliography|Literature Cited|Works Cited|Sources?)\s*\n",
    ]
    
    # Try to find reference section using patterns
    for pattern in patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            start_pos = match.end()
            # Get text from this point to the end
            ref_text = full_text[start_pos:].strip()
            if ref_text and len(ref_text) > 50:  # Ensure we have substantial content
                return ref_text
    
    # Fallback: look for common citation patterns in the last 20% of the document
    # Academic papers typically have references at the end
    last_portion = full_text[-len(full_text)//5:]  # Last 20%
    
    # Look for numbered or lettered lists that might be references
    citation_patterns = [
        r"\n\s*\d+\.\s*[A-Z][^.]*\.\s*\d{4}",  # Numbered references with year
        r"\n\s*[A-Z][a-z]+,\s*[A-Z]\.\s*\d{4}",  # Author, Initial. Year format
        r"\n\s*[A-Z][a-z]+,\s*[A-Z]\.\s*[A-Z][a-z]+,\s*[A-Z]\.\s*\d{4}",  # Multiple authors
        r"\n\s*[A-Z][a-z]+,\s*[A-Z]\.\s*\([^)]*\)",  # Author with parentheses
    ]
    
    for pattern in citation_patterns:
        if re.search(pattern, last_portion, re.MULTILINE):
            # Found citation-like patterns, return the last portion
            return last_portion
    
    # Final fallback: try to extract any text that looks like citations from the entire document
    return _extract_citations_from_full_text(full_text)

def _extract_citations_from_full_text(full_text: str) -> str:
    """
    Fallback method to extract citation-like text from the entire document.
    This is used when no clear reference section is found.
    """
    # Look for patterns that indicate citations throughout the document
    citation_indicators = [
        r'[A-Z][a-z]+,\s*[A-Z]\.\s*\([^)]*\)[^.]*\.\s*[^.]*\.\s*[^,]*,\s*\d+[^,]*,\s*[^.]*',
        r'[A-Z][a-z]+,\s*[A-Z]\.\s*[A-Z][a-z]+,\s*[A-Z]\.\s*\([^)]*\)[^.]*\.\s*[^.]*\.\s*[^,]*,\s*\d+[^,]*,\s*[^.]*',
        r'\n\s*\d+\.\s*[A-Z][^.]*\.\s*\d{4}',
        r'\n\s*[A-Z][a-z]+,\s*[A-Z]\.\s*\d{4}',
    ]
    
    all_citations = []
    for pattern in citation_indicators:
        matches = re.findall(pattern, full_text, re.MULTILINE)
        all_citations.extend(matches)
    
    if all_citations:
        # Return all found citations joined together
        return '\n\n'.join(all_citations)
    
    return ""

def extract_citations_from_references(ref_text: str) -> list[str]:
    """
    Enhanced citation extraction using multiple strategies.
    First tries LLM-based extraction, then falls back to regex-based parsing.
    """
    if not ref_text or len(ref_text.strip()) < 20:
        return []
    
    # Strategy 1: Try LLM-based extraction with a more flexible prompt
    llm_citations = _extract_citations_with_llm(ref_text)
    if llm_citations:
        return llm_citations
    
    # Strategy 2: Fallback to regex-based extraction
    regex_citations = _extract_citations_with_regex(ref_text)
    if regex_citations:
        return regex_citations
    
    return []

def _extract_citations_with_llm(ref_text: str) -> list[str]:
    """
    Use LLM to extract citations with a more flexible approach.
    """
    prompt = f"""
    Extract all citations from this reference section and convert them to BibTeX format.
    
    Rules:
    1. Each citation should be a complete BibTeX entry
    2. Use @article for journal papers, @inproceedings for conference papers, @book for books
    3. Generate a unique key for each entry (e.g., author2024title)
    4. Include all available fields (title, author, year, journal, etc.)
    5. If information is missing, make reasonable assumptions
    
    Reference section:
    {ref_text[:2000]}  # Limit to first 2000 chars to avoid token limits
    
    Return ONLY the BibTeX entries, one per line, starting with @.
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are an expert at converting academic references to BibTeX format. Return only BibTeX entries, no explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse the response to extract BibTeX entries
        bibtex_entries = []
        lines = content.split('\n')
        current_entry = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('@'):
                if current_entry:
                    bibtex_entries.append(current_entry.strip())
                current_entry = line
            elif line and current_entry:
                current_entry += "\n" + line
        
        if current_entry:
            bibtex_entries.append(current_entry.strip())
        
        # Validate entries
        valid_entries = []
        for entry in bibtex_entries:
            if entry.startswith('@') and len(entry) > 20:
                valid_entries.append(entry)
        
        return valid_entries
        
    except Exception as e:
        print(f"Error extracting citations with LLM: {e}")
        return []

def _extract_citations_with_regex(ref_text: str) -> list[str]:
    """
    Fallback method using regex patterns to extract citations.
    """
    citations = []
    
    # Multiple strategies to split citations
    split_strategies = [
        # Strategy 1: Split by numbered references
        r'\n\s*\d+\.\s*',
        # Strategy 2: Split by author patterns
        r'\n\s*[A-Z][a-z]+,\s*[A-Z]\.\s*',
        # Strategy 3: Split by multiple authors
        r'\n\s*[A-Z][a-z]+,\s*[A-Z]\.\s*[A-Z][a-z]+,\s*[A-Z]\.\s*',
        # Strategy 4: Split by bullet points or dashes
        r'\n\s*[-•]\s*',
        # Strategy 5: Split by double newlines (paragraph breaks)
        r'\n\s*\n'
    ]
    
    for strategy in split_strategies:
        lines = re.split(strategy, ref_text)
        if len(lines) > 1:  # Found some splits
            for line in lines:
                line = line.strip()
                if len(line) < 20:  # Skip very short lines
                    continue
                    
                # Try to extract basic citation information
                bibtex_entry = _convert_line_to_bibtex(line)
                if bibtex_entry:
                    citations.append(bibtex_entry)
            
            if citations:  # If we found citations with this strategy, use it
                break
    
    # If no citations found with splitting, try pattern matching on the whole text
    if not citations:
        # Look for citation patterns in the entire reference text
        citation_patterns = [
            r'[A-Z][a-z]+,\s*[A-Z]\.\s*\([^)]*\)[^.]*\.\s*[^.]*\.\s*[^,]*,\s*\d+[^,]*,\s*[^.]*',
            r'[A-Z][a-z]+,\s*[A-Z]\.\s*[A-Z][a-z]+,\s*[A-Z]\.\s*\([^)]*\)[^.]*\.\s*[^.]*\.\s*[^,]*,\s*\d+[^,]*,\s*[^.]*',
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, ref_text)
            for match in matches:
                bibtex_entry = _convert_line_to_bibtex(match)
                if bibtex_entry:
                    citations.append(bibtex_entry)
    
    return citations

def _convert_line_to_bibtex(line: str) -> str:
    """
    Convert a single citation line to BibTeX format using regex patterns.
    """
    # Common patterns for academic citations
    patterns = [
        # Author, A. (Year). Title. Journal, Volume(Issue), Pages.
        r'([A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)\.\s*([^,]*),\s*(\d+)(?:\((\d+)\))?,\s*([^.]*)',
        # Author, A., & Author, B. (Year). Title. Journal, Volume(Issue), Pages.
        r'([A-Z][a-z]+,\s*[A-Z]\.\s*&\s*[A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)\.\s*([^,]*),\s*(\d+)(?:\((\d+)\))?,\s*([^.]*)',
        # Author, A. (Year). Title. Publisher.
        r'([A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)\.\s*([^.]*)',
        # Author, A. (Year). Title. Journal, Volume, Pages.
        r'([A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)\.\s*([^,]*),\s*(\d+),\s*([^.]*)',
        # Author, A. (Year). Title. Journal, Volume(Issue), Pages.
        r'([A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)\.\s*([^,]*),\s*(\d+)\((\d+)\),\s*([^.]*)',
        # Author, A. (Year). Title. Journal, Volume, Issue, Pages.
        r'([A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)\.\s*([^,]*),\s*(\d+),\s*(\d+),\s*([^.]*)',
        # Simple format: Author, A. (Year). Title.
        r'([A-Z][a-z]+,\s*[A-Z]\.)\s*\((\d{4})\)\.\s*([^.]*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            if len(groups) >= 3:
                author = groups[0].replace('&', 'and')
                year = groups[1]
                title = groups[2].strip()
                
                # Generate a key
                author_part = re.sub(r'[^a-zA-Z]', '', author.split(',')[0]).lower()
                title_part = re.sub(r'[^a-zA-Z]', '', title.split()[0]).lower() if title else 'unknown'
                key = f"{author_part}{year}{title_part}"
                
                # Clean up author field (handle & symbol)
                clean_author = author.replace('&', 'and').strip()
                
                # Create BibTeX entry
                bibtex = f"""@article{{{key},
  author = {{{clean_author}}},
  title = {{{title}}},
  year = {{{year}}},"""
                
                # Add journal info if available
                if len(groups) > 3 and groups[3]:
                    journal = groups[3].strip()
                    bibtex += f"\n  journal = {{{journal}}},"
                
                # Add volume if available
                if len(groups) > 4 and groups[4]:
                    volume = groups[4]
                    bibtex += f"\n  volume = {{{volume}}},"
                    
                    # Add issue if available
                    if len(groups) > 5 and groups[5]:
                        issue = groups[5]
                        bibtex += f"\n  number = {{{issue}}},"
                
                # Add pages if available
                if len(groups) > 6 and groups[6]:
                    pages = groups[6].strip()
                    bibtex += f"\n  pages = {{{pages}}},"
                
                bibtex += "\n}"
                return bibtex
    
    return ""

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
        # Fallback: try to extract basic fields manually
        return _extract_bibtex_fields_manual(bibtex_str)
    return {}

def _extract_bibtex_fields_manual(bibtex_str: str) -> dict:
    """
    Manual extraction of BibTeX fields as fallback.
    """
    fields = {}
    
    # Extract key
    key_match = re.search(r'@\w+\{([^,]+),', bibtex_str)
    if key_match:
        fields['ID'] = key_match.group(1)
    
    # Extract author
    author_match = re.search(r'author\s*=\s*\{([^}]+)\}', bibtex_str)
    if author_match:
        fields['author'] = author_match.group(1)
    
    # Extract title
    title_match = re.search(r'title\s*=\s*\{([^}]+)\}', bibtex_str)
    if title_match:
        fields['title'] = title_match.group(1)
    
    # Extract year
    year_match = re.search(r'year\s*=\s*\{([^}]+)\}', bibtex_str)
    if year_match:
        fields['year'] = year_match.group(1)
    
    # Extract journal
    journal_match = re.search(r'journal\s*=\s*\{([^}]+)\}', bibtex_str)
    if journal_match:
        fields['journal'] = journal_match.group(1)
    
    # Extract DOI
    doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', bibtex_str)
    if doi_match:
        fields['doi'] = doi_match.group(1)
    
    return fields