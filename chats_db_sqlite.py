""" 
chats_db_sqlite.py
This module provides functions for creating a SQLite database, saving chat sessions, loading saved chats, loading chat messages, and deleting chats.
"""
import sqlite3
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chats_db_sqlite")

DATABASE_NAME = 'chats.db'

def create_database():
    """Create the database and required tables if they do not exist."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    chat_name TEXT,
                    messages TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    username TEXT PRIMARY KEY,
                    preferred_model TEXT DEFAULT 'llama3.1'
                )
            ''')

            conn.commit()
            logger.info("Database and tables setup completed successfully")
    except sqlite3.Error as e:
        logger.error(f"Error accessing database: {e}")
        raise

def save_chat(username, chat_name, messages):
    """Save a chat of a specific user with the given name and messages."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO chats (username, chat_name, messages) VALUES (?, ?, ?)', 
                           (username, chat_name, json.dumps(messages)))
            conn.commit()
            logger.info(f"Chat '{chat_name}' saved successfully for user '{username}'")
    except sqlite3.Error as e:
        logger.error(f"Error saving chat: {e}")
        raise

def load_chats(username):
    """Load all chats for a specific user from the database."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, chat_name, username FROM chats WHERE username = ?', (username,))
            chats = cursor.fetchall()
        logger.info(f"Successfully loaded {len(chats)} chats for user '{username}'")
        return chats
    except sqlite3.Error as e:
        logger.error(f"Error loading chats: {e}")
        raise

def load_chat_messages(chat_id, username):
    """Load messages for a specific chat by ID for a specific user."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT messages FROM chats WHERE id = ? AND username = ?', (chat_id, username))
            result = cursor.fetchone()
            if result:
                messages = json.loads(result[0])
                logger.info(f"Successfully loaded messages for chat ID {chat_id} for user '{username}'")
                return True, messages
            else:
                logger.warning(f"No chat found with id: {chat_id} for user '{username}'")
                return False, None
    except sqlite3.Error as e:
        logger.error(f"Error loading chat messages: {e}")
        raise

def delete_chat(chat_id, username):
    """Delete a chat by ID for a specific user."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chats WHERE id = ? AND username = ?', (chat_id, username))
            conn.commit()
            logger.info(f"Chat with ID {chat_id} deleted successfully for user '{username}'")
    except sqlite3.Error as e:
        logger.error(f"Error deleting chat: {e}")
        raise

# Functions to handle user preferences
def save_user_preference(username, preferred_model):
    """Save the preferred model for a specific user."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (username, preferred_model)
                VALUES (?, ?)
            ''', (username, preferred_model))
            conn.commit()
            logger.info(f"Preference saved for user '{username}': model '{preferred_model}'")
    except sqlite3.Error as e:
        logger.error(f"Error saving user preference: {e}")
        raise

def get_user_preference(username):
    """Get the preferred model for a specific user."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT preferred_model FROM user_preferences WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return 'llama3.1'  # Default model if not set
    except sqlite3.Error as e:
        logger.error(f"Error getting user preference: {e}")
        raise
