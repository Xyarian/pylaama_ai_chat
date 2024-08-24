""" 
PyLaama AI Chat - A Streamlit based app for chatting with the AI LLM models
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import ollama
import base64
import pdfplumber
from docx import Document
# SQLite database functions (comment out to use PostgreSQL)
from chats_db_sqlite import create_database, save_chat, load_chats, load_chat_messages, delete_chat, save_user_preference, get_user_preference
# PostgreSQL database functions (uncomment to use PostgreSQL)
# from chats_db_postgres import create_database, save_chat, load_chats, load_chat_messages, delete_chat, save_user_preference, get_user_preference
import logging
import datetime as dt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("laama_chat")

# Set page title, favicon, layout, etc.
st.set_page_config(
    page_title="PyLaama AI Chat",
    page_icon="🦙",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "# PyLaama AI Chat v0.2.0-alpha  \nBy Xyarian 2024  \nhttps://github.com/Xyarian"
    }
)

# Load the app configuration from the config.yaml file
try:
    with open('auth/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    logger.error("Authentication configuration file not found! Please create a config.yaml file in the auth folder.")
    st.error("❗⚠️ Authentication configuration file not found!")
    st.stop()
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    st.error(f"Error loading configuration: {e}")
    st.stop()

# Pre-hashing all plain text passwords once
# Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

def login_tab():
    name, authentication_status, username = authenticator.login(
        location='main',
        fields={
            'Form name': 'Login',
            'Username': 'Username',
            'Password': 'Password',
            'Login': '🔐 Login'
        }
    )
    
    if st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        #st.info('Please enter your username and password to login.')
        pass

def register_tab():
    """Register a new user with the Streamlit Authenticator and update the config.yaml file."""
    try:
        # Register the user and get their details
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
            pre_authorization=False,
            fields={
                'Form name': 'Register',
                'Name': 'Name',
                'Email': 'Email',
                'Username': 'Username',
                'Password': 'Password (8 to 20 characters, at least one of each: a-z, A-Z, 0-9, @$!%*?&)',
                'Repeat password': 'Repeat password',
                'Register': '🔑 Register'
            },
            captcha=True
        )

        if email_of_registered_user:
            st.success('User registered successfully!')

            try:
                with open('auth/config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(f"Error saving configuration: {e}")

    except Exception as e:
        st.error(e)

def account_page():
    """Display the account settings page with options to select AI model, reset password and update user details."""
    if st.button("🔙 Back to Chat", help="Return to the main chat interface", key="back_to_chat"):
        st.session_state['show_account_page'] = False
        st.rerun()

    st.title("Account Settings")
    st.write(f"Logged in as: ***{st.session_state['name']}*** (***{st.session_state['username']}***)")

    # Model Selection
    st.header("Select AI Model")
    current_model = get_user_preference(st.session_state['username'])
    models = ["llama3.1", "gemma2"]  # Add more models as needed
    selected_model = st.selectbox("Choose your preferred AI model:", models, index=models.index(current_model))
    
    if selected_model != current_model:
        save_user_preference(st.session_state['username'], selected_model)
        logger.info(f"User '{st.session_state['username']}' updated AI model preference to '{selected_model}'")
        st.success(f"AI model preference updated to {selected_model}")

    st.divider()

    # Reset Password Widget
    st.header("Reset Password")
    try:
        if authenticator.reset_password(st.session_state['username'], 'main'):
            try:
                with open('auth/config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('Password modified successfully')
            except Exception as e:
                st.error(f"Error saving configuration: {e}")
    except Exception as e:
        st.error(e)

    st.divider()

    # Update User Details Widget
    st.header("Update User Details")
    try:
        if authenticator.update_user_details(st.session_state['username'], 'main'):
            try:
                with open('auth/config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('User details updated successfully')
            except Exception as e:
                st.error(f"Error saving configuration: {e}")
    except Exception as e:
        st.error(e)

def get_greeting_message():
    """Get a greeting message based on the current time of day."""
    current_hour = dt.datetime.now().hour
    if current_hour < 5:
        return f"Good night, {st.session_state['name']}!"
    elif current_hour < 12:
        return f"Good morning, {st.session_state['name']}!"
    elif current_hour < 18:
        return f"Good afternoon, {st.session_state['name']}!"
    elif current_hour < 22:
        return f"Good evening, {st.session_state['name']}!"
    else:
        return f"Hello, {st.session_state['name']}!"

def extract_text(file, file_type):
    """Extract text content from a file based on its MIME type."""
    try:
        if file_type == "application/pdf":
            return extract_text_from_pdf(file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(file)
        elif file_type in ["text/plain", "text/x-python", "text/bat", "text/cmd", "text/sh"]:
            return file.read().decode('utf-8')
        else:
            st.error("Unsupported file type.")
            return ""
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

def extract_text_from_docx(file):
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_pdf(file):
    """Extract text from a PDF file using pdfplumber."""
    try:
        text = ''
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    st.warning("Some pages may not contain extractable text.")
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def get_ai_response(messages):
    """Get a response from the AI model based on the user messages."""
    try:
        with st.spinner("PyLaama is thinking..."):
            model = get_user_preference(st.session_state['username'])
            response = ollama.chat(
                model=model, #  Model to use for the chat (llama3.1, gemma2, etc.) 
                messages=messages,
            )
        return response['message']['content']
    except Exception as e:
        logger.error(f"PyLaama response error: {e}")
        return "I'm sorry, I couldn't process your request."

def load_image(image_file):
    """Load an image and convert it to a Base64 string."""
    try:
        with open(image_file, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        logger.error("Background image file not found.")
        return ""

def apply_custom_css(css_file, b64_image, image_ext):
    """Load custom CSS from a file and apply it with a background image."""
    try:
        with open(css_file, "r") as file:
            css = file.read()
        st.markdown(
            f"""
            <style>
            /* Custom CSS styles for the PyLaama AI Chat app */
            [data-testid="stHeader"] {{
                background-color: rgba(14, 17, 23, 0.8) !important;
                color: #ffffff !important;
            }}
            /* Style for the app with background image */
            .stApp {{
                background-image: url('data:image/{image_ext};base64,{b64_image}');
            }}
            {css}
            /* Styles for input fields */
            [data-testid="stTextInput-RootElement"] {{
                background-color: rgba(14, 17, 23, 0.5) !important;
            }}
            [data-baseweb="base-input"] {{
                background-color: rgba(14, 17, 23, 0.1) !important;
            }}
            /* Styles for chat message avatars */
            [data-testid="chatAvatarIcon-user"] {{
                background-color: #42e59e !important;
            }}
            [data-testid="chatAvatarIcon-assistant"] {{
                background-color: #8f3dd0 !important;  /* #aa58e8 */
            }}
            /* Style for sidebar */
            [data-testid="stSidebar"] {{
                background-color: rgba(14, 17, 23, 0.8) !important;
            }}
            /* Style for file uploader */
            [data-testid="stFileUploaderDropzone"] {{
                background-color: rgba(14, 17, 23, 0.5) !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        logger.error("CSS file not found.")

def load_saved_chats():
    """Load saved chats from the database for the current user."""
    try:
        return load_chats(st.session_state["username"])
    except Exception as e:
        st.error(f"Error loading chats: {e}")
        return []

def delete_chat_callback(chat_id, chat_name):
    """Callback function to delete a chat by ID of the current user."""
    try:
        delete_chat(chat_id, st.session_state["username"])
        st.session_state.saved_chats = load_saved_chats()
        st.toast(f"Successfully deleted chat ***{chat_name}***.", icon="🗑️")
    except Exception as e:
        st.error(f"Error deleting chat: {e}")

@st.cache_resource
def initialize_database():
    try:
        create_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def main():
    """Main function for the PyLaama AI Chat app."""
    # Load the background image and custom CSS
    image_file = "files/bg_image.png"  # Background image file path
    image_ext = "png"  # Background image file extension
    b64_image = load_image(image_file) # Load the background image as Base64

    # Apply the custom CSS with the background image
    apply_custom_css("css/styles.css", b64_image, image_ext)

    # Check if the user is already authenticated
    if not st.session_state['authentication_status']:
        st.title("PyLaama AI Chat")
        # Create tabs for Login and Register
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            login_tab()
        with tab2:
            register_tab()

    # Check if the user is authenticated
    if st.session_state['authentication_status']:
        # Initialize database
        initialize_database()

        # Initialize chat history
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []

        # Load saved chats for the current user
        if 'saved_chats' not in st.session_state:
            try:
                st.session_state.saved_chats = load_saved_chats()
            except Exception as e:
                st.error(f"Error loading chats: {e}")
                st.session_state.saved_chats = []
        else:
            # Refresh saved chats on each run to ensure up-to-date data
            st.session_state.saved_chats = load_saved_chats()

        # Load user's preferred model
        if 'preferred_model' not in st.session_state:
            st.session_state['preferred_model'] = get_user_preference(st.session_state['username'])
            logger.info(f"Init: User '{st.session_state['username']}' prefers model '{st.session_state['preferred_model']}'")

        # Get the user's preferred model
        #current_model = get_user_preference(st.session_state['username'])

        # Check if the account page should be shown
        if 'show_account_page' not in st.session_state:
            st.session_state['show_account_page'] = False

        # Sidebar with the app title and account controls
        st.sidebar.header("PyLaama AI Chat - Menu", divider=True)

        # Logout and Account Buttons in the Sidebar
        if st.session_state['authentication_status']:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if not st.session_state['show_account_page']:
                    if st.button('👤 Account', help='Access the user account settings page', use_container_width=True):
                        st.session_state['show_account_page'] = True
                else:
                    if st.button('🤖 Chat View', help='Switch back to the main chat interface', use_container_width=True):
                        st.session_state['show_account_page'] = False
            with col2:
                if st.button('↪️ Logout', help='Log out of the current account', use_container_width=True):
                    logger.info("Logout button clicked.")

                    # Clear the current chat session on logout
                    if 'messages' in st.session_state:
                        logger.info(st.session_state['messages'])
                        del st.session_state['messages']
                    if 'saved_chats' in st.session_state:
                        del st.session_state['saved_chats']
                        
                    st.session_state['authentication_status'] = None  # Manually set to logged out state
                    logger.info("User logged out. Session state cleared.")
                    st.rerun()  # Refresh the app to show the login form

        st.sidebar.divider()
        st.sidebar.header("Chat Controls", help="Manage your current chat session", divider=True)

        # Sidebar with a "New Chat" button
        new_chat_button = st.sidebar.button("🆕 New Chat", help="Start a new chat session and clear the current conversation")

        # Clear current chat session if the "New Chat" button is clicked
        if new_chat_button:
            st.session_state['messages'] = []
            st.toast("You can start a new conversation.", icon="✅")
            st.toast("Chat session cleared.", icon="🗑️")

        # Save Chat Section with form
        with st.sidebar.form("save_chat_form"):
            chat_name = st.text_input("Enter a chat name for saving:", placeholder="My Chat", max_chars=50)
            submit_button = st.form_submit_button("💾 Save Chat", help="Save the current chat with a custom name")

        if submit_button:
            if chat_name:
                try:
                    save_chat(st.session_state["username"], chat_name, st.session_state['messages'])
                    st.sidebar.success("Chat saved successfully!")
                    st.toast(f"Chat ***{chat_name}*** saved successfully.", icon="✅")
                    st.session_state.saved_chats = load_saved_chats()
                except Exception as e:
                    st.sidebar.error(f"Error saving chat: {e}")
            else:
                st.sidebar.warning("Please enter a chat name before saving.")

        # Saved Chats Section
        st.sidebar.subheader("Saved Chats", help="Load or delete saved chats", divider=True)
        for chat_id, chat_name, chat_username in st.session_state.saved_chats:
            if chat_username == st.session_state["username"]:
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    if st.button(f"{chat_name}", help="Load the saved chat", key=f"load_{chat_id}", use_container_width=True):
                        try:
                            success, messages = load_chat_messages(chat_id, st.session_state["username"])
                            if success:
                                st.session_state['messages'] = messages
                                if messages:
                                    st.toast(f"Successfully loaded messages for chat ***{chat_name}***.", icon="✅")
                                else:
                                    st.toast(f"Chat ***{chat_name}*** has been loaded but contains no messages.", icon="ℹ️")
                        except Exception as e:
                            st.error(f"Error loading chat messages: {e}")
                with col2:
                    if st.button("🗑️", help="Delete the saved chat", key=f"delete_{chat_id}", on_click=delete_chat_callback, args=(chat_id, chat_name)):
                        pass

        # Set the initial state of the account settings page
        if 'show_account_page' not in st.session_state:
            st.session_state['show_account_page'] = False

        # Check if the account settings page should be shown
        if st.session_state['show_account_page']:
            # Display the account settings page
            account_page()
        else:
            # Display the main chat page
            # Display the personalized greeting
            greeting_message = get_greeting_message()
            st.write(greeting_message)

            # Get the user's preferred model
            current_model = get_user_preference(st.session_state['username'])

            # Display the chat interface with the title and welcome message
            st.title('PyLaama AI Chat')
            st.write(f"Welcome to PyLaama AI Chat with the **{current_model}**! Ask me anything or share a document to get started.")

            # File uploader for adding files to the chat context
            uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "bat", "cmd", "sh", "py",])
            if uploaded_file is not None:
                file_content = extract_text(uploaded_file, uploaded_file.type)

                if file_content:
                    st.session_state['messages'].append({"role": "system", "content": file_content})
                    st.success("File content added to context.")
                else:
                    st.warning("The file appears to be empty or unreadable.")

            # Display chat messages from history on app rerun
            for message in st.session_state['messages']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input for user prompts/messages
            if prompt := st.chat_input("Message PyLaama..."):
                st.session_state['messages'].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                ai_response = get_ai_response(st.session_state['messages'])
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                st.session_state['messages'].append({"role": "assistant", "content": ai_response})

    # Save the app configuration to the config.yaml file
    with open('auth/config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

if __name__ == "__main__":
    main()
