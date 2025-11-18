import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import config

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                agreed_to_terms INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Coupons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                type INTEGER NOT NULL,
                price INTEGER NOT NULL,
                is_sold INTEGER DEFAULT 0,
                sold_to INTEGER,
                sold_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sold_to) REFERENCES users (user_id)
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                coupon_type INTEGER NOT NULL,
                price INTEGER NOT NULL,
                gift_card_code TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                coupon_id INTEGER,
                verified_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (coupon_id) REFERENCES coupons (id)
            )
        ''')

        # Bot settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Support messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Initialize bot status as offline
        cursor.execute('''
            INSERT OR IGNORE INTO bot_settings (key, value)
            VALUES ('bot_online', '0')
        ''')

        conn.commit()
        conn.close()

    # User Management
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_active)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name))
        conn.commit()
        conn.close()

    def user_agreed_to_terms(self, user_id: int):
        """Mark user as agreed to terms"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET agreed_to_terms = 1
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()

    def has_user_agreed(self, user_id: int) -> bool:
        """Check if user agreed to terms"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT agreed_to_terms FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 1

    def get_all_users(self) -> List[int]:
        """Get all user IDs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users

    # Coupon Management
    def add_coupon(self, code: str, coupon_type: int, price: int):
        """Add a new coupon"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO coupons (code, type, price)
                VALUES (?, ?, ?)
            ''', (code, coupon_type, price))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_available_stock(self) -> Dict[int, int]:
        """Get count of available coupons by type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT type, COUNT(*) FROM coupons
            WHERE is_sold = 0
            GROUP BY type
        ''')
        stock = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return stock

    def get_available_coupon(self, coupon_type: int) -> Optional[int]:
        """Get an available coupon of specified type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM coupons
            WHERE type = ? AND is_sold = 0
            LIMIT 1
        ''', (coupon_type,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def mark_coupon_sold(self, coupon_id: int, user_id: int):
        """Mark coupon as sold"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE coupons
            SET is_sold = 1, sold_to = ?, sold_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id, coupon_id))
        conn.commit()
        conn.close()

    def get_coupon_code(self, coupon_id: int) -> Optional[str]:
        """Get coupon code by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT code FROM coupons WHERE id = ?', (coupon_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # Transaction Management
    def create_transaction(self, user_id: int, coupon_type: int, price: int, gift_card_code: str) -> int:
        """Create a new transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (user_id, coupon_type, price, gift_card_code)
            VALUES (?, ?, ?, ?)
        ''', (user_id, coupon_type, price, gift_card_code))
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id

    def get_pending_transactions(self) -> List[Dict]:
        """Get all pending transactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.user_id, u.username, u.first_name,
                   t.coupon_type, t.price, t.gift_card_code, t.created_at
            FROM transactions t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.status = 'pending'
            ORDER BY t.created_at DESC
        ''')
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'first_name': row[3],
                'coupon_type': row[4],
                'price': row[5],
                'gift_card_code': row[6],
                'created_at': row[7]
            })
        conn.close()
        return transactions

    def approve_transaction(self, transaction_id: int, coupon_id: int, verified_by: int):
        """Approve a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET status = 'approved', coupon_id = ?, verified_by = ?, verified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (coupon_id, verified_by, transaction_id))
        conn.commit()
        conn.close()

    def reject_transaction(self, transaction_id: int, verified_by: int):
        """Reject a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET status = 'rejected', verified_by = ?, verified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (verified_by, transaction_id))
        conn.commit()
        conn.close()

    def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        """Get transaction by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, coupon_type, price, gift_card_code, status, coupon_id
            FROM transactions WHERE id = ?
        ''', (transaction_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'coupon_type': result[2],
                'price': result[3],
                'gift_card_code': result[4],
                'status': result[5],
                'coupon_id': result[6]
            }
        return None

    # Bot Settings
    def set_bot_online(self, online: bool):
        """Set bot online/offline status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bot_settings SET value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE key = 'bot_online'
        ''', ('1' if online else '0',))
        conn.commit()
        conn.close()

    def is_bot_online(self) -> bool:
        """Check if bot is online"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM bot_settings WHERE key = 'bot_online'")
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == '1'

    def update_offline_message(self, message: str):
        """Update offline message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
            VALUES ('offline_message', ?, CURRENT_TIMESTAMP)
        ''', (message,))
        conn.commit()
        conn.close()

    def get_offline_message(self) -> str:
        """Get custom offline message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM bot_settings WHERE key = 'offline_message'")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else config.OFFLINE_MESSAGE

    # Support Messages
    def add_support_message(self, user_id: int, message: str):
        """Add support message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO support_messages (user_id, message)
            VALUES (?, ?)
        ''', (user_id, message))
        conn.commit()
        conn.close()

    def get_unread_support_messages(self) -> List[Dict]:
        """Get unread support messages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sm.id, sm.user_id, u.username, u.first_name, sm.message, sm.created_at
            FROM support_messages sm
            JOIN users u ON sm.user_id = u.user_id
            WHERE sm.is_read = 0
            ORDER BY sm.created_at DESC
        ''')
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'first_name': row[3],
                'message': row[4],
                'created_at': row[5]
            })
        conn.close()
        return messages

    def mark_support_message_read(self, message_id: int):
        """Mark support message as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE support_messages SET is_read = 1 WHERE id = ?', (message_id,))
        conn.commit()
        conn.close()

    # Statistics
    def get_stats(self) -> Dict:
        """Get sales statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total sales
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'approved'")
        total_sales = cursor.fetchone()[0]

        # Total revenue
        cursor.execute("SELECT SUM(price) FROM transactions WHERE status = 'approved'")
        total_revenue = cursor.fetchone()[0] or 0

        # Pending transactions
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'pending'")
        pending = cursor.fetchone()[0]

        # Available stock by type
        cursor.execute('''
            SELECT type, COUNT(*) FROM coupons
            WHERE is_sold = 0
            GROUP BY type
        ''')
        stock = {row[0]: row[1] for row in cursor.fetchall()}

        # Total users
        cursor.execute("SELECT COUNT(*) FROM users WHERE agreed_to_terms = 1")
        total_users = cursor.fetchone()[0]

        conn.close()

        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'pending_transactions': pending,
            'stock': stock,
            'total_users': total_users
        }

# Create global database instance
db = Database()
