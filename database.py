import sqlite3
import logging
from datetime import datetime

DB_PATH = "visa_bot.db"
logger = logging.getLogger(__name__)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    try:
        with get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id     INTEGER PRIMARY KEY,
                    username    TEXT,
                    first_name  TEXT,
                    joined_at   TEXT NOT NULL,
                    clicked_wa  INTEGER NOT NULL DEFAULT 0,
                    click_count INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS clicks (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER NOT NULL,
                    username    TEXT,
                    source      TEXT,
                    clicked_at  TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS followups (
                    user_id     INTEGER PRIMARY KEY,
                    started_at  TEXT NOT NULL,
                    sent_10min  INTEGER NOT NULL DEFAULT 0,
                    sent_1hr    INTEGER NOT NULL DEFAULT 0,
                    sent_6hr    INTEGER NOT NULL DEFAULT 0,
                    stopped     INTEGER NOT NULL DEFAULT 0
                );
            """)
        logger.info("Database initialised.")
    except Exception as exc:
        logger.error("DB init error: %s", exc)


def upsert_user(user_id: int, username: str | None, first_name: str | None) -> None:
    try:
        with get_conn() as conn:
            existing = conn.execute(
                "SELECT user_id FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO users (user_id, username, first_name, joined_at) VALUES (?,?,?,?)",
                    (user_id, username, first_name, datetime.utcnow().isoformat()),
                )
            else:
                conn.execute(
                    "UPDATE users SET username=?, first_name=? WHERE user_id=?",
                    (username, first_name, user_id),
                )
    except Exception as exc:
        logger.error("upsert_user error: %s", exc)


def record_wa_click(user_id: int, username: str | None, source: str = "button") -> None:
    try:
        with get_conn() as conn:
            conn.execute(
                "UPDATE users SET clicked_wa=1, click_count=click_count+1 WHERE user_id=?",
                (user_id,),
            )
            conn.execute(
                "INSERT INTO clicks (user_id, username, source, clicked_at) VALUES (?,?,?,?)",
                (user_id, username, source, datetime.utcnow().isoformat()),
            )
            conn.execute(
                "UPDATE followups SET stopped=1 WHERE user_id=?", (user_id,)
            )
    except Exception as exc:
        logger.error("record_wa_click error: %s", exc)


def init_followup(user_id: int) -> None:
    try:
        with get_conn() as conn:
            existing = conn.execute(
                "SELECT user_id FROM followups WHERE user_id=?", (user_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO followups (user_id, started_at) VALUES (?,?)",
                    (user_id, datetime.utcnow().isoformat()),
                )
    except Exception as exc:
        logger.error("init_followup error: %s", exc)


def get_followup_row(user_id: int) -> sqlite3.Row | None:
    try:
        with get_conn() as conn:
            return conn.execute(
                "SELECT * FROM followups WHERE user_id=?", (user_id,)
            ).fetchone()
    except Exception as exc:
        logger.error("get_followup_row error: %s", exc)
        return None


def mark_followup_sent(user_id: int, stage: str) -> None:
    try:
        with get_conn() as conn:
            conn.execute(
                f"UPDATE followups SET {stage}=1 WHERE user_id=?", (user_id,)
            )
    except Exception as exc:
        logger.error("mark_followup_sent error: %s", exc)


def get_all_users() -> list[sqlite3.Row]:
    try:
        with get_conn() as conn:
            return conn.execute("SELECT * FROM users").fetchall()
    except Exception as exc:
        logger.error("get_all_users error: %s", exc)
        return []


def get_stats() -> dict:
    try:
        with get_conn() as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_clicks = conn.execute("SELECT COUNT(*) FROM clicks").fetchone()[0]
            converted = conn.execute(
                "SELECT COUNT(*) FROM users WHERE clicked_wa=1"
            ).fetchone()[0]
            top_users = conn.execute(
                "SELECT username, first_name, click_count FROM users ORDER BY click_count DESC LIMIT 5"
            ).fetchall()
        conversion_rate = (converted / total_users * 100) if total_users else 0
        return {
            "total_users": total_users,
            "total_clicks": total_clicks,
            "converted": converted,
            "conversion_rate": round(conversion_rate, 2),
            "top_users": [dict(r) for r in top_users],
        }
    except Exception as exc:
        logger.error("get_stats error: %s", exc)
        return {}
