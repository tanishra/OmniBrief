"""
src/persistence.py
Enhanced SQLite history tracking for OmniBrief.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = "digest_history.db"

def init_db():
    """Initializes the SQLite database with enhanced metadata."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # sent_items: Permanent history to prevent duplicates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_items (
            url TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            section TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def load_history() -> set:
    """Loads sent URLs into a set for fast lookup."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM sent_items")
    history = {row[0] for row in cursor.fetchall()}
    conn.close()
    return history

def is_duplicate(url: str, history_set: set = None) -> bool:
    """Checks if a URL has already been sent using a direct SQL query."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_items WHERE url = ?", (url,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def mark_sent(url: str, title: str = "", source: str = "", section: str = ""):
    """Saves item with metadata to history."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO sent_items (url, title, source, section) VALUES (?, ?, ?, ?)",
            (url, title, source, section)
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def cleanup_history(days: int = 14):
    """Removes old entries to keep DB lean (increased to 14 days)."""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sent_items WHERE sent_at < ?", (cutoff,))
    conn.commit()
    conn.close()
