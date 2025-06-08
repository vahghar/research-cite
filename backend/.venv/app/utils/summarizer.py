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