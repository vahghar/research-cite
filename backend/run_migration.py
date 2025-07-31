#!/usr/bin/env python3
"""
Simple script to add the eli5_summary column to the summaries table.
Run this if alembic is not working properly.
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Add eli5_summary column to summaries table"""
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'summaries' AND column_name = 'eli5_summary'
            """))
            
            if result.fetchone():
                print("Column 'eli5_summary' already exists in summaries table.")
                return
            
            # Add the column
            conn.execute(text("ALTER TABLE summaries ADD COLUMN eli5_summary TEXT"))
            conn.commit()
            print("Successfully added 'eli5_summary' column to summaries table.")
            
    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 