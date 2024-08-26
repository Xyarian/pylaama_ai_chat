"""
chats_db_postgres.py
This module provides functions for creating a PostgreSQL database, saving chat sessions, loading saved chats, loading chat messages, and deleting chats.
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chats_db_postgres")

# Get PostgreSQL connection details from Streamlit secrets in .streamlit/secrets.toml
pg_config = st.secrets.connections.postgresql

# Database connection URL
DATABASE_URL = f"postgresql://{pg_config.username}:{pg_config.password}@{pg_config.host}:{pg_config.port}/{pg_config.database}"

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
    messages = Column(Text)

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
    """Save a chat of a specific user with the given name and messages."""
    with Session() as session:
        with session.begin():
            try:
                new_chat = Chat(username=username, chat_name=chat_name, messages=json.dumps(messages))
                session.add(new_chat)
                logger.info(f"Chat '{chat_name}' saved successfully for user '{username}'")
            except SQLAlchemyError as e:
                logger.error(f"Error saving chat: {e}")
                raise

@retryable_query
def load_chats(username):
    """Load all chats for a specific user from the database."""
    with Session() as session:
        try:
            chats = session.query(Chat.id, Chat.chat_name, Chat.username).filter(Chat.username == username).all()
            logger.info(f"Successfully loaded {len(chats)} chats for user '{username}'")
            return chats
        except SQLAlchemyError as e:
            logger.error(f"Error loading chats: {e}")
            raise

@retryable_query
def load_chat_messages(chat_id, username):
    """Load messages for a specific chat by ID for a specific user."""
    with Session() as session:
        try:
            chat = session.query(Chat).filter(Chat.id == chat_id, Chat.username == username).first()
            if chat:
                messages = json.loads(chat.messages)
                logger.info(f"Successfully loaded messages for chat ID {chat_id} for user '{username}'")
                return True, messages
            else:
                logger.warning(f"No chat found with id: {chat_id} for user '{username}'")
                return False, None
        except SQLAlchemyError as e:
            logger.error(f"Error loading chat messages: {e}")
            raise

@retryable_query
def delete_chat(chat_id, username):
    """Delete a chat by ID for a specific user."""
    with Session() as session:
        with session.begin():
            try:
                chat = session.query(Chat).filter(Chat.id == chat_id, Chat.username == username).first()
                if chat:
                    session.delete(chat)
                    logger.info(f"Chat with ID {chat_id} deleted successfully for user '{username}'")
                else:
                    logger.warning(f"No chat found with id: {chat_id} for user '{username}'")
            except SQLAlchemyError as e:
                logger.error(f"Error deleting chat: {e}")
                raise

@retryable_query
def save_user_preference(username, preferred_model):
    """Save or update a user's preferred model."""
    with Session() as session:
        with session.begin():
            try:
                preference = session.query(UserPreference).filter(UserPreference.username == username).first()
                if preference:
                    preference.preferred_model = preferred_model
                else:
                    preference = UserPreference(username=username, preferred_model=preferred_model)
                    session.add(preference)
                logger.info(f"Preference saved for user '{username}': model '{preferred_model}'")
            except SQLAlchemyError as e:
                logger.error(f"Error saving user preference: {e}")
                raise

@retryable_query
def get_user_preference(username):
    """Get a user's preferred model."""
    with Session() as session:
        try:
            preference = session.query(UserPreference).filter(UserPreference.username == username).first()
            if preference:
                return preference.preferred_model
            else:
                return 'llama3.1'  # Default model if not set
        except SQLAlchemyError as e:
            logger.error(f"Error getting user preference: {e}")
            raise
        