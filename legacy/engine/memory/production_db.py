# engine/memory/production_db.py
import os
import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ProductionDatabase:
    """
    Persistent Production Database for GenOTT V2.
    Tracks characters, scenes, shots, assets, generation history, checkpoints, model versions,
    voice assets, and final renders using SQLite.
    """

    def __init__(self, db_file: str = "movie_projects/genott_production.db"):
        self.db_file = os.path.abspath(db_file)
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self.init_tables()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE,
                    logline TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    production_title TEXT,
                    shot_id INTEGER,
                    prompt TEXT,
                    backend TEXT,
                    video_path TEXT,
                    quality_score REAL,
                    generation_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    seed INTEGER,
                    vram_gb REAL,
                    latency_sec REAL,
                    status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def record_production(self, title: str, logline: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO productions (title, logline) VALUES (?, ?)", (title, logline))
            conn.commit()

    def record_shot_render(self, title: str, shot_id: int, prompt: str, backend: str, video_path: str, quality_score: float, gen_time: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO shots (production_title, shot_id, prompt, backend, video_path, quality_score, generation_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, shot_id, prompt, backend, video_path, quality_score, gen_time)
            )
            conn.commit()

    def get_history(self, title: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shots WHERE production_title = ? ORDER BY shot_id ASC", (title,))
            return [dict(row) for row in cursor.fetchall()]
