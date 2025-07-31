# app/api/routes.py

import os
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..crud import document as crud_doc
from ..crud import summary as crud_sum
from ..crud import citation as crud_cit
from ..crud import user as crud_user
from ..schemas.document import DocumentCreate, DocumentRead, DocumentStatusResponse
from ..schemas.summary import SummaryRead
from ..schemas.citation import CitationRead
from ..api.dependencies import get_current_user
from ..models.document import DocumentStatus
from ..core.config import settings
from ..schemas.user import UserRead, UserCreate, Token, UserLogin
from app.api.dependencies import create_access_token
from ..tasks.process_document import process_document
from ..utils.summarizer import generate_eli5_summary
from ..utils.pdf_parser import extract_text_from_pdf
from ..utils import research_paper_recommender

router = APIRouter(prefix="/documents", tags=["documents"])
auth_router = APIRouter(prefix="/auth",tags=["auth"])

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

#authroutes
@auth_router.post("/signup",response_model=UserRead,status_code=status.HTTP_201_CREATED)
def signup(user_in:UserCreate,db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db,email = user_in.email)
    if db_user:
        raise HTTPException(status_code=400,detail="User already exists")
    user = crud_user.create_user(db,user_in)
    return user

@auth_router.post("/login",response_model=Token,status_code=status.HTTP_200_OK)
async def login_for_access_token(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db,email = user_credentials.email)
    if not user or not crud_user.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=400,detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


#documentroutes
@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(None),
    doc_in: DocumentCreate = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Either accept a file upload, or a JSON body with source_url.
    If file is provided, save it and ignore source_url. If URL is provided instead,
    download it to local upload folder.
    """
    if file is None and not doc_in.source_url:
        raise HTTPException(status_code=400, detail="Must provide file or source_url.")

    # Ensure the uploads/owner_id/ folder exists
    user_folder = os.path.join(UPLOAD_FOLDER, str(current_user.id))
    os.makedirs(user_folder, exist_ok=True)

    if file:
        # Save uploaded file
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        dest_path = os.path.join(user_folder, unique_name)
        with open(dest_path, "wb") as buffer:
            buffer.write(await file.read())
        doc = crud_doc.create_document(db, owner_id=current_user.id, file_path=dest_path, original_filename=file.filename)
    else:
        # Download from URL (arXiv/DOI). For simplicity, we just store the URL and let Celery download it.
        doc = crud_doc.create_document(db, owner_id=current_user.id, file_path="", original_filename="", source_url=doc_in.source_url)

    try:
        print(f"--- DEBUG: Document created with ID: {doc.id}, File Path: {doc.file_path} ---") # Added print
        print(f"--- DEBUG: Attempting to call process_document for doc ID: {doc.id} ---") # Added print
        db.refresh(doc)
        process_document(None, doc.id) # Pass None for 'self' since it's not a Celery task
        print(f"--- DEBUG: process_document call finished for doc ID: {doc.id} ---") # Added print
        return doc
    except Exception as e:
        print(f"--- DEBUG: Exception caught in upload_document for doc ID {doc.id}: {e} ---") # Added print
        import traceback
        traceback.print_exc() # Print full traceback to console
        raise HTTPException(status_code=500, detail="Error processing document.")



@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    print(f"DEBUG: Getting document {document_id} for user {current_user.id}")
    db_doc = crud_doc.get_document(db, document_id)
    print(f"DEBUG: Document found: {db_doc is not None}")
    if db_doc:
        print(f"DEBUG: Document owner: {db_doc.owner_id}, Current user: {current_user.id}")
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    return db_doc

@router.get("/{document_id}/summary", response_model=SummaryRead)
def fetch_summary(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    if db_doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Document is not yet processed.")
    db_summary = crud_sum.get_summary_by_document(db, document_id)
    if not db_summary:
        raise HTTPException(status_code=404, detail="Summary not found.")
    return db_summary

@router.get("/{document_id}/citations", response_model=List[CitationRead])
def fetch_citations(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    if db_doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Document is not yet processed.")
    citations = crud_cit.get_citations_by_document(db, document_id)
    return citations

@router.get("/{document_id}/recommendations")
def recommend_research_papers(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Recommend research papers based on the document's summary (or full text if summary not available).
    """
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    if db_doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Document is not yet processed.")
    db_summary = crud_sum.get_summary_by_document(db, document_id)
    if db_summary:
        text = " ".join([
            db_summary.introduction or "",
            db_summary.methods or "",
            db_summary.results or "",
            db_summary.conclusion or "",
        ])
    else:
        from ..utils.pdf_parser import extract_text_from_pdf
        text = extract_text_from_pdf(db_doc.file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text available for recommendations.")
    papers = research_paper_recommender.recommend_papers(text)
    return {"recommendations": papers}

@router.post("/{document_id}/eli5", response_model=SummaryRead)
def generate_eli5_summary_endpoint(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Generate an ELI5 (Explain Like I'm 5) summary for a document.
    """
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    if db_doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Document is not yet processed.")
    
    # Check if summary exists
    db_summary = crud_sum.get_summary_by_document(db, document_id)
    if not db_summary:
        raise HTTPException(status_code=404, detail="Summary not found.")
    
    try:
        # Extract text from PDF
        full_text = extract_text_from_pdf(db_doc.file_path)
        
        # Generate ELI5 summary
        eli5_summary = generate_eli5_summary(full_text)
        
        # Update the summary with ELI5 content
        updated_summary = crud_sum.update_eli5_summary(db, document_id, eli5_summary)
        
        return updated_summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ELI5 summary: {str(e)}")

@router.post("/{document_id}/push_zotero")
def push_to_zotero(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Take all Citation rows for this document and push them to Zotero using the user's stored API key.
    In production, you may need to handle OAuth token refreshing, etc.
    """
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not current_user.zotero_api_key or not current_user.zotero_user_id:
        raise HTTPException(status_code=400, detail="Zotero credentials not configured.")
    citations = crud_cit.get_citations_by_document(db, document_id)
    added_count = 0
    from ..oauth_utils import push_citation_to_zotero
    for cit in citations:
        success = push_citation_to_zotero(current_user.zotero_user_id, current_user.zotero_api_key, cit.raw_bibtex)
        if success:
            added_count += 1
    return {"success": True, "added_count": added_count}

@router.delete("/{document_id}/summary", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    if db_doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Document is not yet processed.")
    db_summary = crud_sum.get_summary_by_document(db, document_id)
    if not db_summary:
        raise HTTPException(status_code=404, detail="Summary not found.")
    
    crud_sum.delete_summary(db, db_summary.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Delete a document and all its related data (summary, citations, and file).
    """
    print(f"Delete request for document {document_id} from user {current_user.id}")
    
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        print(f"Document {document_id} not found or user {current_user.id} not authorized")
        raise HTTPException(status_code=404, detail="Document not found.")
    
    print(f"Attempting to delete document {document_id}")
    success = crud_doc.delete_document(db, document_id)
    if not success:
        print(f"Failed to delete document {document_id}")
        raise HTTPException(status_code=500, detail="Failed to delete document.")
    
    print(f"Successfully deleted document {document_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/", response_model=List[DocumentRead])
def get_all_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    documents = crud_doc.get_documents_by_owner(db, owner_id=current_user.id)
    return documents



