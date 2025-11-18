"""
Database module for Contact Bot
Stores messages and conversation history
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import contact_bot_config as config


class ContactDatabase:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                first_contact TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contact TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                from_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_contact)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name, last_name))

        conn.commit()
        conn.close()

    def add_message(self, user_id: int, message_text: str, from_admin: bool = False):
        """Add a message to history"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO messages (user_id, message_text, from_admin)
            VALUES (?, ?, ?)
        ''', (user_id, message_text, 1 if from_admin else 0))

        # Update user's last contact time
        cursor.execute('''
            UPDATE users SET last_contact = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

    def get_conversation_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get conversation history with a user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT message_text, from_admin, created_at
            FROM messages
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'text': row[0],
                'from_admin': row[1] == 1,
                'timestamp': row[2]
            })

        conn.close()
        return list(reversed(messages))  # Oldest first

    def get_active_conversations(self, limit: int = 50) -> List[Dict]:
        """Get list of users who have messaged"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.user_id, u.username, u.first_name, u.last_name, u.last_contact,
                   COUNT(m.id) as message_count
            FROM users u
            LEFT JOIN messages m ON u.user_id = m.user_id
            GROUP BY u.user_id
            ORDER BY u.last_contact DESC
            LIMIT ?
        ''', (limit,))

        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'last_contact': row[4],
                'message_count': row[5]
            })

        conn.close()
        return conversations

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, username, first_name, last_name, first_contact, last_contact
            FROM users
            WHERE user_id = ?
        ''', (user_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'first_contact': result[4],
                'last_contact': result[5]
            }
        return None

    def get_total_users(self) -> int:
        """Get total number of users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_total_messages(self) -> int:
        """Get total number of messages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM messages')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_all_user_ids(self) -> List[int]:
        """Get all user IDs for broadcasting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return user_ids


# Create global database instance
db = ContactDatabase()
