import sqlite3
import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from typing import Optional, List, Tuple
from datetime import datetime

# Load environment variables
load_dotenv()
OWNER_USER_ID = int(os.getenv('OWNER_USER_ID', 0))

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'anonymous_bot.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        join_date TEXT,
                        is_blocked INTEGER DEFAULT 0
                    )
                ''')
                
                # Messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        message TEXT,
                        timestamp TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # For easier column access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def add_user(self, user_id: int, username: Optional[str] = None, 
                      first_name: Optional[str] = None, last_name: Optional[str] = None) -> bool:
        """Add or update user in database"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, join_date, is_blocked)
                    VALUES (?, ?, ?, ?, ?, 
                           COALESCE((SELECT is_blocked FROM users WHERE user_id = ?), 0))
                ''', (user_id, username, first_name, last_name, 
                     datetime.now().isoformat(), user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user_info(self, user_id: int) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get user information"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT username, first_name, last_name FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if result:
                    return result['username'], result['first_name'], result['last_name']
                return None, None, None
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return None, None, None
    
    async def find_user_by_username(self, username: str) -> Optional[int]:
        """Find user by username"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
                result = cursor.fetchone()
                return result['user_id'] if result else None
        except Exception as e:
            logger.error(f"Error finding user by username {username}: {e}")
            return None
    
    async def get_user_by_username(self, username: str):
        """Get user by username"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
                result = cursor.fetchone()
                return result if result else None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    async def save_message(self, user_id: int, message: str) -> bool:
        """Save message to database"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (user_id, message, timestamp)
                    VALUES (?, ?, ?)
                ''', (user_id, message, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving message for user {user_id}: {e}")
            return False
    
    async def get_all_users(self):
        """Get list of all users (excluding admin)"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, last_name, join_date, is_blocked 
                    FROM users WHERE user_id != ? ORDER BY join_date DESC
                ''', (OWNER_USER_ID,))
                return [(row['user_id'], row['username'], row['first_name'], 
                        row['last_name'], row['join_date'], row['is_blocked']) 
                       for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
        
    async def get_system_stats(self):
        """Get system statistics (excluding admin)"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total users (excluding admin)
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_id != ?', (OWNER_USER_ID,))
                total_users = cursor.fetchone()['count']
                
                # Active users (not blocked and excluding admin)
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_blocked = 0 AND user_id != ?', (OWNER_USER_ID,))
                active_users = cursor.fetchone()['count']
                
                # Blocked users (excluding admin)
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_blocked = 1 AND user_id != ?', (OWNER_USER_ID,))
                blocked_users = cursor.fetchone()['count']
                
                # Total messages (excluding admin messages)
                cursor.execute('SELECT COUNT(*) as count FROM messages WHERE user_id != ?', (OWNER_USER_ID,))
                total_messages = cursor.fetchone()['count']
                
                return total_users, active_users, blocked_users, total_messages
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return 0, 0, 0, 0
        
    async def get_active_users(self):
        """Get list of active users (excluding admin)"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE is_blocked = 0 AND user_id != ?', (OWNER_USER_ID,))
                return [row['user_id'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def get_all_users_detailed(self) -> List[Tuple[int, str, str, str, int]]:
        """Get all users with detailed information (excluding admin)"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, last_name, is_blocked 
                    FROM users WHERE user_id != ? ORDER BY join_date DESC
                ''', (OWNER_USER_ID,))
                return [(row['user_id'], row['username'], row['first_name'], 
                        row['last_name'], row['is_blocked']) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users detailed: {e}")
            return []
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                if exclude_blocked:
                    cursor.execute('SELECT user_id FROM users WHERE is_blocked = 0')
                else:
                    cursor.execute('SELECT user_id FROM users')
                return [row['user_id'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_user_count(self) -> int:
        """Get total user count"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_blocked = 0')
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def get_blocked_users(self):
        """Get list of blocked users"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, last_name 
                    FROM users WHERE is_blocked = 1 AND user_id != ? 
                    ORDER BY join_date DESC
                ''', (OWNER_USER_ID,))
                return [(row['user_id'], row['username'], row['first_name'], row['last_name']) 
                       for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting blocked users: {e}")
            return []
    
    async def get_stats(self):
        """Get system statistics"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total number of users (excluding admin)
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE user_id != ?', (OWNER_USER_ID,))
                total_users = cursor.fetchone()['count']
                
                # Active users
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_blocked = 0 AND user_id != ?', (OWNER_USER_ID,))
                active_users = cursor.fetchone()['count']
                
                # Blocked users
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_blocked = 1 AND user_id != ?', (OWNER_USER_ID,))
                blocked_users = cursor.fetchone()['count']
                
                # Total number of messages
                cursor.execute('SELECT COUNT(*) as count FROM messages')
                total_messages = cursor.fetchone()['count']
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'blocked_users': blocked_users,
                    'total_messages': total_messages
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'blocked_users': 0,
                'total_messages': 0
            }
    
    async def get_all_users_detailed(self) -> List[Tuple[int, str, str, str, int]]:
        """Get all users with detailed information"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, last_name, is_blocked 
                    FROM users ORDER BY join_date DESC
                ''')
                return [(row['user_id'], row['username'], row['first_name'], 
                        row['last_name'], row['is_blocked']) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users detailed: {e}")
            return []

    async def block_user(self, user_id: int) -> bool:
        """Block a user"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                logger.info(f"User {user_id} blocked successfully")
                return True
        except Exception as e:
            logger.error(f"Error blocking user {user_id}: {e}")
            return False
    
    async def unblock_user(self, user_id: int) -> bool:
        """Unblock a user"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
                conn.commit()
                logger.info(f"User {user_id} unblocked successfully")
                return True
        except Exception as e:
            logger.error(f"Error unblocking user {user_id}: {e}")
            return False

    async def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT is_blocked FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                return bool(result['is_blocked']) if result else False
        except Exception as e:
            logger.error(f"Error checking if user {user_id} is blocked: {e}")
            return False

# Global database instance
db_manager = DatabaseManager()