import sqlite3
import json
from datetime import datetime

DB_PATH = "genott.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            script      TEXT NOT NULL,
            genre       TEXT NOT NULL,
            style       TEXT NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS scenes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL,
            scene_num   INTEGER NOT NULL,
            title       TEXT,
            type        TEXT,
            setting     TEXT,
            mood        TEXT,
            characters  TEXT,
            duration    TEXT,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_id     INTEGER NOT NULL,
            video_prompt TEXT NOT NULL,
            FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables ready.")


# ── PROJECTS ──

def save_project(title, script, genre, style, scenes_data):
    """Save a project + all its scenes + prompts. Returns project id."""
    conn = get_db()
    c = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    c.execute(
        "INSERT INTO projects (title, script, genre, style, created_at) VALUES (?,?,?,?,?)",
        (title, script, genre, style, created_at)
    )
    project_id = c.lastrowid

    for i, scene in enumerate(scenes_data, start=1):
        c.execute("""
            INSERT INTO scenes
            (project_id, scene_num, title, type, setting, mood, characters, duration, description)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            project_id,
            i,
            scene.get("title", ""),
            scene.get("type", ""),
            scene.get("setting", ""),
            scene.get("mood", ""),
            scene.get("characters", ""),
            scene.get("duration", ""),
            scene.get("description", ""),
        ))
        scene_id = c.lastrowid

        video_prompt = scene.get("video_prompt", "")
        if video_prompt:
            c.execute(
                "INSERT INTO prompts (scene_id, video_prompt) VALUES (?,?)",
                (scene_id, video_prompt)
            )

    conn.commit()
    conn.close()
    return project_id


def get_all_projects():
    conn = get_db()
    c = conn.cursor()
    rows = c.execute(
        "SELECT id, title, genre, style, created_at FROM projects ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(project_id):
    conn = get_db()
    c = conn.cursor()

    project = c.execute(
        "SELECT * FROM projects WHERE id=?", (project_id,)
    ).fetchone()

    if not project:
        conn.close()
        return None

    scenes = c.execute(
        "SELECT * FROM scenes WHERE project_id=? ORDER BY scene_num", (project_id,)
    ).fetchall()

    result = dict(project)
    result["scenes"] = []

    for scene in scenes:
        scene_dict = dict(scene)
        prompt_row = c.execute(
            "SELECT video_prompt FROM prompts WHERE scene_id=?", (scene["id"],)
        ).fetchone()
        scene_dict["video_prompt"] = prompt_row["video_prompt"] if prompt_row else ""
        result["scenes"].append(scene_dict)

    conn.close()
    return result


def delete_project(project_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()
