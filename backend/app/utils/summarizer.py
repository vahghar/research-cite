# app/utils/summarizer.py

import os
import json
from groq import Groq
from .pdf_parser import split_text_into_chunks
from ..core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_structured_summary(full_text: str) -> dict:
    """
    Generate a structured summary of a scientific paper using Groq AI.
    """
    prompt = f"""
    You are a scientific paper summarizer. Given the full text of a research paper,
    return a JSON object with exactly these keys (no extra keys):
    {{
      "introduction": "<~100-word summary of introduction section>",
      "methods": "<~100-word summary of methods section>",
      "results": "<~100-word summary of results section>",
      "conclusion": "<~100-word summary of conclusion section>"
    }}
    Only summarize content in those sections; if a section is missing, leave it as an empty string.
    Full text:
    \"\"\"
    {full_text}
    \"\"\"
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # e.g., "mixtral-8x7b-32768" or "llama2-70b-4096"
            messages=[
                {"role": "system", "content": "You are a helpful summarizer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            summary_json = json.loads(content)
            # Ensure all required keys are present
            for key in ["introduction", "methods", "results", "conclusion"]:
                if key not in summary_json:
                    summary_json[key] = ""
            return summary_json
        except json.JSONDecodeError:
            return {"introduction": "", "methods": "", "results": "", "conclusion": ""}
            
    except Exception as e:
        print(f"Error generating summary with Groq: {e}")
        return {"introduction": "", "methods": "", "results": "", "conclusion": ""}

def generate_eli5_summary(full_text: str) -> str:
    """
    Generate an ELI5 (Explain Like I'm 5) summary of a scientific paper using Groq AI.
    """
    prompt = f"""
    You are an expert at explaining complex scientific concepts in simple terms that a 5-year-old could understand.
    
    Given the full text of a research paper, create a simple, engaging explanation that:
    1. Uses simple, everyday language
    2. Avoids technical jargon
    3. Uses analogies and examples a child would understand
    4. Explains what the researchers were trying to figure out
    5. Explains what they found in simple terms
    6. Explains why it matters in everyday life
    
    Keep it under 300 words and make it fun and engaging!
    
    Full text:
    \"\"\"
    {full_text}
    \"\"\"
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are an expert at explaining complex topics in simple terms."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()
            
    except Exception as e:
        print(f"Error generating ELI5 summary with Groq: {e}")
        return "Sorry, I couldn't create a simple explanation right now. Please try again later."