import json
import sqlite3


class SQLiteMemory:
    def __init__(self, connection_string: str):
        self.connection = sqlite3.connect(connection_string)

    def insert_session_id(self, guid: str, user: str, title: str):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO sessions (guid, user, title)
            VALUES (?, ?, ?)
            ON CONFLICT(guid) DO NOTHING
            """,
            (guid, user, title),
        )

        self.connection.commit()

    def get_user_sessions(self, user: str) -> list:
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT guid, title
            FROM sessions
            WHERE user = ?
            ORDER BY created_at DESC
            """,
            (user,),
        )

        return cursor.fetchall()

    def save_messages(self, guid: str, messages: list):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE sessions
            SET messages = ?
            WHERE guid = ?
        """,
            (json.dumps(messages), guid),
        )

        self.connection.commit()

    def get_messages(self, guid: str) -> list:
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT messages
            FROM sessions
            WHERE guid = ?
        """,
            (guid,),
        )

        row = cursor.fetchone()

        if row and row[0]:
            return json.loads(row[0])

        return []

    def append_message(self, guid: str, new_message: dict):
        messages = self.get_messages(guid)
        messages.append(new_message)
        self.save_messages(guid, messages)
