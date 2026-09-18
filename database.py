"""
SQLite storage for meetings and their extracted action items.
Keeping this separate from the LangChain logic so the DB schema
can evolve without touching the LLM chains.
"""
import sqlite3
from datetime import datetime

DB_PATH = "meetings.db"


def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            summary TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            task TEXT,
            owner TEXT,
            deadline TEXT,
            priority TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (meeting_id) REFERENCES meetings (id)
        )
    """)
    conn.commit()
    conn.close()


def add_meeting(title: str, date: str, summary: str, db_path: str = DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO meetings (title, date, summary, created_at) VALUES (?, ?, ?, ?)",
        (title, date, summary, datetime.now().isoformat()),
    )
    meeting_id = cur.lastrowid
    conn.commit()
    conn.close()
    return meeting_id


def add_action_items(meeting_id: int, items: list, db_path: str = DB_PATH):
    """items: list of dicts with keys task, owner, deadline, priority"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for item in items:
        cur.execute(
            """INSERT INTO action_items (meeting_id, task, owner, deadline, priority)
               VALUES (?, ?, ?, ?, ?)""",
            (meeting_id, item["task"], item["owner"], item["deadline"], item["priority"]),
        )
    conn.commit()
    conn.close()


def get_all_meetings(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM meetings ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_action_items(meeting_id: int = None, status: str = None, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = """
        SELECT action_items.*, meetings.title as meeting_title
        FROM action_items JOIN meetings ON action_items.meeting_id = meetings.id
        WHERE 1=1
    """
    params = []
    if meeting_id is not None:
        query += " AND meeting_id = ?"
        params.append(meeting_id)
    if status is not None:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY action_items.id DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def update_status(action_item_id: int, status: str, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE action_items SET status = ? WHERE id = ?", (status, action_item_id))
    conn.commit()
    conn.close()
