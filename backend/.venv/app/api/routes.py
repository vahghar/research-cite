# app/api/routes.py

import os
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
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
        process_document(None, doc.id) # Pass None for 'self' since it's not a Celery task
        db.refresh(doc)
        print(f"--- DEBUG: process_document call finished for doc ID: {doc.id} ---") # Added print
        return doc
    except Exception as e:
        print(f"--- DEBUG: Exception caught in upload_document for doc ID {doc.id}: {e} ---") # Added print
        import traceback
        traceback.print_exc() # Print full traceback to console
        raise HTTPException(status_code=500, detail="Error processing document.")

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(document_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_doc = crud_doc.get_document(db, document_id)
    if not db_doc or db_doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentStatusResponse(
        id=db_doc.id,
        status=db_doc.status,
        progress=db_doc.progress
    )

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
