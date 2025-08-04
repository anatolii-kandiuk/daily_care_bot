import sqlite3
from datetime import datetime

class TodoManager:
    def __init__(self, db_name="data/todo.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    user_id INTEGER,
                    task TEXT,
                    is_done INTEGER DEFAULT 0,
                    date TEXT,
                    created_at TEXT,
                    completed_at TEXT
                )
            ''')

    def add_task(self, user_id, task, date):
        created_at = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                INSERT INTO todos (user_id, task, is_done, date, created_at)
                VALUES (?, ?, 0, ?, ?)
            """, (user_id, task, date, created_at))

    def get_dates(self, user_id):
        cursor = self.conn.execute("""
            SELECT DISTINCT date FROM todos WHERE user_id=? ORDER BY date
        """, (user_id,))
        return [row[0] for row in cursor.fetchall()]

    def get_tasks(self, user_id, date):
        cursor = self.conn.execute("""
            SELECT task, is_done FROM todos WHERE user_id=? AND date=?
        """, (user_id, date))
        return cursor.fetchall()

    def delete_task(self, user_id, date, index):
        tasks = self.get_tasks(user_id, date)
        if 0 <= index < len(tasks):
            task_text = tasks[index][0]
            with self.conn:
                self.conn.execute("""
                    DELETE FROM todos WHERE user_id=? AND date=? AND task=?
                """, (user_id, date, task_text))

    def mark_done(self, user_id, date, index):
        tasks = self.get_tasks(user_id, date)
        if 0 <= index < len(tasks):
            task_text = tasks[index][0]
            completed_at = datetime.now().isoformat()
            with self.conn:
                self.conn.execute("""
                    UPDATE todos
                    SET is_done=1, completed_at=?
                    WHERE user_id=? AND date=? AND task=?
                """, (completed_at, user_id, date, task_text))
    
    def get_all_users_with_tasks(self, date_str):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT user_id FROM todos WHERE date = ?", (date_str,))
        rows = cur.fetchall()
        return [row[0] for row in rows]