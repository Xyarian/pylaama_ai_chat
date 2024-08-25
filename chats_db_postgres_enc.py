"""
chats_db_postgres_enc.py
This module provides functions for creating an encrypted PostgreSQL database, saving chat sessions, loading saved chats, loading chat messages, and deleting chats.
"""
import streamlit as st
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, DatabaseError, InternalError, OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from functools import wraps
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.sql import func

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chats_db_postgres_enc")

# Database connection URL from Streamlit secrets in .streamlit/secrets.toml or environment variables
DATABASE_URL = f"postgresql://{st.secrets.connections.postgresql.enc.username}:{st.secrets.connections.postgresql.enc.password}@{st.secrets.connections.postgresql.enc.host}:{st.secrets.connections.postgresql.enc.port}/{st.secrets.connections.postgresql.enc.database}"

# SECRET (!) encryption key from Streamlit secrets in .streamlit/secrets.toml or environment variables
encryption_key = st.secrets.connections.postgresql.enc.key

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for declarative models
Base = declarative_base()

# Define the Chat model
class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    chat_name = Column(String)
    encrypted_messages = Column(BYTEA)

# Define the UserPreference model
class UserPreference(Base):
    __tablename__ = 'user_preferences'

    username = Column(String, primary_key=True)
    preferred_model = Column(String, default='llama3.1')

# Create a session factory
Session = sessionmaker(bind=engine)

def retryable_query(func):
    """Decorator to retry a function if a database error occurs."""
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type((DatabaseError, InternalError, OperationalError)),
        reraise=True
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@retryable_query
def create_database():
    """Create the database and required tables if they do not exist."""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database and tables setup completed successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database: {e}")
        raise

@retryable_query
def save_chat(username, chat_name, messages):
    """Save a chat of a specific user with the given name and messages using encryption."""
    try:
        session = Session()
        encrypted = func.pgp_sym_encrypt(json.dumps(messages), encryption_key)
        new_chat = Chat(username=username, chat_name=chat_name, encrypted_messages=encrypted)
        session.add(new_chat)
        session.commit()
        logger.info(f"Chat '{chat_name}' saved successfully for user '{username}'")
    except SQLAlchemyError as e:
        logger.error(f"Error saving chat: {e}")
        session.rollback()
        raise
    finally:
        session.close()

@retryable_query
def load_chats(username):
    """Load all chats for a specific user from the database."""
    try:
        session = Session()
        chats = session.query(Chat.id, Chat.chat_name, Chat.username).filter(Chat.username == username).all()
        logger.info(f"Successfully loaded {len(chats)} chats for user '{username}'")
        return chats
    except SQLAlchemyError as e:
        logger.error(f"Error loading chats: {e}")
        raise
    finally:
        session.close()

@retryable_query
def load_chat_messages(chat_id, username):
    """Load messages for a specific chat by ID for a specific user using decryption."""
    try:
        session = Session()
        query = session.query(
            func.pgp_sym_decrypt(Chat.encrypted_messages, encryption_key).label('decrypted')
        ).filter(Chat.id == chat_id, Chat.username == username)
        result = query.first()
        if result:
            messages = json.loads(result.decrypted)
            logger.info(f"Successfully loaded messages for chat ID {chat_id} for user '{username}'")
            return True, messages
        else:
            logger.warning(f"No chat found with id: {chat_id} for user '{username}'")
            return False, None
    except SQLAlchemyError as e:
        logger.error(f"Error loading chat messages: {e}")
        raise
    finally:
        session.close()

@retryable_query
def delete_chat(chat_id, username):
    """Delete a chat by ID for a specific user."""
    try:
        session = Session()
        chat = session.query(Chat).filter(Chat.id == chat_id, Chat.username == username).first()
        if chat:
            session.delete(chat)
            session.commit()
            logger.info(f"Chat with ID {chat_id} deleted successfully for user '{username}'")
        else:
            logger.warning(f"No chat found with id: {chat_id} for user '{username}'")
    except SQLAlchemyError as e:
        logger.error(f"Error deleting chat: {e}")
        session.rollback()
        raise
    finally:
        session.close()

@retryable_query
def save_user_preference(username, preferred_model):
    """Save or update a user's preferred model."""
    try:
        session = Session()
        preference = session.query(UserPreference).filter(UserPreference.username == username).first()
        if preference:
            preference.preferred_model = preferred_model
        else:
            preference = UserPreference(username=username, preferred_model=preferred_model)
            session.add(preference)
        session.commit()
        logger.info(f"Preference saved for user '{username}': model '{preferred_model}'")
    except SQLAlchemyError as e:
        logger.error(f"Error saving user preference: {e}")
        session.rollback()
        raise
    finally:
        session.close()

@retryable_query
def get_user_preference(username):
    """Get a user's preferred model."""
    try:
        session = Session()
        preference = session.query(UserPreference).filter(UserPreference.username == username).first()
        if preference:
            return preference.preferred_model
        else:
            return 'llama3.1'  # Default model if not set
    except SQLAlchemyError as e:
        logger.error(f"Error getting user preference: {e}")
        raise
    finally:
        session.close()


# Notes on PostgreSQL Encryption with pgcrypto:
# ---------------------------------------------

# 1. Enabling pgcrypto:
#    a) Connect to your database using one of these methods:
#       - If not logged in: psql -d your_database_name
#       - If already logged into psql: \c your_database_name
#    b) Enable the extension: CREATE EXTENSION IF NOT EXISTS pgcrypto;
#    c) Verify installation: \dx
#    Note: This needs to be done once per database, requires superuser privileges.

# 2. Verifying encryption:
#    In psql, run: SELECT * FROM chats;
#    The 'encrypted_messages' column should contain binary data.

# 3. Decrypting messages:
#    In psql, replace 'your_encryption_key_here' with your actual key:
#    SELECT pgp_sym_decrypt(encrypted_messages::bytea, 'your_encryption_key_here') FROM chats;
#    Or for more context:
#    SELECT id, username, chat_name, pgp_sym_decrypt(encrypted_messages::bytea, 'your_encryption_key_here') as decrypted_messages FROM chats;

# 4. Key Management:
#    - This app uses Streamlit local app secrets (.streamlit/secrets.toml) to store the encryption key as well as the database connection URL. 
#    - For local use, this is sufficient, but remember not to share this file.
#    - If you are using Streamlit Community Cloud, Secrets management allows you save environment variables and store secrets outside of your code. 
#    - If you are using another platform designed for Streamlit, check if they have a built-in mechanism for working with secrets. 
#    - Consider using environment variables or secure vaults for key storage in production.

# 5. Performance Impact:
#    - Encryption/decryption operations can impact database performance.
#    - This is more pronounced in larger datasets.

# 6. Limitations:
#    - Database-level encryption doesn't protect against all threats.
#    - Data is decrypted when retrieved, so application-level security is still crucial.

# 7. Security Considerations (for future reference):
#    - While this setup is suitable for learning, production environments require additional security measures.
#    - The encryption key is stored in the same place as the application, which wouldn't be ideal for production.
#    - Topics to explore: secure key management, access controls, and data protection regulations.

# 8. Alternatives:
#    - Consider application-level encryption for more granular control.
#    - Evaluate full-disk encryption for comprehensive data-at-rest protection.

# For more information:
# - PostgreSQL pgcrypto documentation: https://www.postgresql.org/docs/current/pgcrypto.html
# - OWASP Cryptographic Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
