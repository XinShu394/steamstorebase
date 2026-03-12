"""
Database Migration: Add categories_json and genres_json columns
"""
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path("data/steam_data.db")
    
    if not db_path.exists():
        print("Database does not exist yet. No migration needed.")
        return
    
    print("Starting migration: Adding categories_json and genres_json columns...")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(games)")
        columns = [row[1] for row in cursor.fetchall()]
        
        needs_migration = False
        
        if "categories_json" not in columns:
            print("  - Adding categories_json column...")
            cursor.execute("ALTER TABLE games ADD COLUMN categories_json TEXT")
            needs_migration = True
        else:
            print("  - categories_json column already exists")
        
        if "genres_json" not in columns:
            print("  - Adding genres_json column...")
            cursor.execute("ALTER TABLE games ADD COLUMN genres_json TEXT")
            needs_migration = True
        else:
            print("  - genres_json column already exists")
        
        if needs_migration:
            conn.commit()
            print("\n[OK] Migration completed successfully!")
        else:
            print("\n[OK] No migration needed - all columns exist")

if __name__ == "__main__":
    migrate()
