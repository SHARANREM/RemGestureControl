import sqlite3
import os
from utils.logger import logger

class Database:
    """
    Handles SQLite database connection and table creation.
    """
    def __init__(self, db_path: str = "gesture_config.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a new connection to the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes the database schema if it doesn't exist."""
        schema = [
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS gestures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER,
                gesture_name TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                confirm BOOLEAN DEFAULT 0,
                confirmation_message TEXT,
                FOREIGN KEY (app_id) REFERENCES applications (id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gesture_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                config_json TEXT NOT NULL,
                execution_order INTEGER NOT NULL,
                FOREIGN KEY (gesture_id) REFERENCES gestures (id) ON DELETE CASCADE
            )
            """
        ]
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for statement in schema:
                    cursor.execute(statement)
                
                # Ensure 'global' app exists
                cursor.execute("INSERT OR IGNORE INTO applications (name) VALUES ('global')")
                conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
