import uvicorn
from fastapi import FastAPI
from app.api.routes import router as document_router, auth_router
# If you have an auth router (e.g. for /auth/token), import and include it here:
# from app.api.auth import auth_router

app = FastAPI(
    title="AI‐Powered Literature Summarizer & Citation Extractor",
    description=(
        "Upload PDFs or provide arXiv/DOI links, then get back a structured summary "
        "(Introduction/Methods/Results/Conclusion) and an extracted citation index in BibTeX/APA formats."
    ),
    version="0.1.0",
)

# Include the document‐processing router under /documents
app.include_router(document_router)
app.include_router(auth_router)

# (Optional) If you create an auth router later:
# app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/", tags=["health"])
async def root():
    """
    Simple health check endpoint.
    """
    return {"message": "Literature Summarizer API is up and running."}

if __name__ == "__main__":
    # Run with: python -m uvicorn app.main:app --reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
