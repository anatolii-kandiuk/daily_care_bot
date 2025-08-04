import sqlite3
from pathlib import Path

DB_PATH = Path("data/users.db")

class TodoManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    user_id INTEGER,
                    task TEXT,
                    is_done INTEGER DEFAULT 0
                )
            """)

    def add_task(self, user_id, task):
        with self.conn:
            self.conn.execute(
                "INSERT INTO todos (user_id, task, is_done) VALUES (?, ?, 0)",
                (user_id, task)
            )

    def get_tasks(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT task, is_done FROM todos WHERE user_id = ?", (user_id,))
        return cur.fetchall()

    def delete_task(self, user_id, index):
        tasks = self.get_tasks(user_id)
        if 0 <= index < len(tasks):
            task_to_delete = tasks[index][0]
            with self.conn:
                self.conn.execute(
                    "DELETE FROM todos WHERE user_id = ? AND task = ? LIMIT 1",
                    (user_id, task_to_delete)
                )

    def mark_done(self, user_id, index):
        tasks = self.get_tasks(user_id)
        if 0 <= index < len(tasks):
            task_to_mark = tasks[index][0]
            with self.conn:
                self.conn.execute(
                    "UPDATE todos SET is_done = 1 WHERE user_id = ? AND task = ?",
                    (user_id, task_to_mark)
                )
