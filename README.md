# PyLaama AI Chat

**PyLaama AI Chat** is an interactive **chat interface** built with [Streamlit](https://streamlit.io/), designed to harness the power of Large Language Models (LLMs) for AI-driven conversations. The application leverages [Ollama](https://ollama.ai/) to run various LLM models **locally**, with default support for [Meta Llama 3.1 8B](https://llama.meta.com/) *(default model)* and [Google Gemma 2 9B](https://ai.google.dev/gemma) models to provide intelligent, context-aware responses.

## Features

- 🤖 **Interactive AI Chat**: Chat interface for dynamic conversations with sophisticated AI models
- 🔄 **Model Flexibility**: Easily switch between different LLM models supported by Ollama
- 📄 **Document Context**: Document upload support to provide additional context for more informed AI responses
- 💾 **Session Management**: Save, load, and manage multiple chat sessions for continuity and reference
- 👤 **Multi-User Support**: Basic authentication system allowing multiple users to maintain separate chat histories and preferences
- 🎨 **User-Friendly Interface**: Custom-styled Streamlit-powered UI for interaction
- 🛠️ **Database Handling**: Custom database action functions implemented for SQLite and PostgreSQL, independent of Streamlit's `st.connection`, keeping portability across platforms

**PyLaama AI Chat** combines cutting-edge AI technology with practical features, making it ideal for **learning, and exploration** in the realm of Artificial Intelligence and Natural Language Processing (NLP).

## Installation

### Prerequisites

- Python
- Ollama
- *Optional: PostgreSQL for advanced database functionality; SQLite is used by default*

[![Python Version](https://img.shields.io/badge/Python-3.12.5-yellow)](https://www.python.org/downloads/)
[![Ollama Version](https://img.shields.io/badge/Ollama-0.3.5-green)](https://ollama.ai)
[![Streamlit Version](https://img.shields.io/badge/Streamlit-1.37.1-red)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue)](https://www.postgresql.org/)

### Setup

1. Install Ollama and the AI models:
Follow the instructions at [Ollama's official website](https://ollama.ai/) or https://github.com/ollama/ollama to install Ollama and download the LLM model(s). E.g. once Ollama is installed:

```
ollama pull llama3.1
```

and / or

```
ollama pull gemma2
```

**Note:** You can pull any model supported by Ollama. Check [Ollama's model library](https://ollama.ai/library) for more options.

2. Clone the repository:

```
git clone https://github.com/Xyarian/pylaama_ai_chat.git
cd pylaama_ai_chat
```

3. Create a virtual environment:

- Windows:

  ```
  python -m venv .venv
  .venv\Scripts\activate
  ```

- Linux/macOS:

  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

4. Install dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Rename the `auth/config.yaml.example` file to `auth/config.yaml`.

2. Run the Streamlit app:

```
streamlit run laama_chat.py
```

3. Open your web browser and navigate to the URL displayed in the terminal (`http://localhost:8501`).

4. Log in using the default user credentials provided in the `auth/config.yaml` file or register a new user.

5. Start chatting with PyLaama, upload documents, or use the sidebar to manage chat sessions.

6. In the user account settings, you can choose your preferred AI model from the available options pulled from Ollama.

## Customizing AI Models

PyLaama AI Chat uses Ollama to run LLM models **locally**. By default, it supports Llama 3.1 and Gemma 2, but you can easily add support for any model available in Ollama:

1. Pull the desired model using Ollama:

```
ollama pull model_name
```

2. Add the model name to the list of available models in `laama_chat.py`.

For a list of available models and their capabilities, visit [Ollama's model library](https://ollama.ai/library).

## Project Structure

```
pylaama_ai_chat /
├── .streamlit/
│   └── config.toml
│   └── secrets.toml(.example)
├── auth/
│   └── config.yaml(.example)
├── css/
│   └── styles.css
├── files/
│   └── bg_image.png
├── chats_db_postgres_enc.py
├── chats_db_postgresql.py
├── chats_db_sqlite3.py
├── laama_chat.py
└── requirements.txt

```

### Dependencies

See `requirements.txt` for a list of Python dependencies.

### Acknowledgements

- [Llama 3.1](https://llama.meta.com/)
- [Gemma 2](https://ai.google.dev/gemma)
- [Ollama](https://ollama.ai/)
- [Streamlit](https://streamlit.io/)
- [Streamlit-Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)
- [PostgreSQL](https://www.postgresql.org/)

### Screenshots

![Screenshot 1](https://github.com/user-attachments/assets/36f0168e-ccf0-43c7-8862-3fa54d4dd2cc)

![Screenshot 2](https://github.com/user-attachments/assets/52ec8457-2dab-4412-8bcf-f31ad5c7e42e)

![Screenshot 3](https://github.com/user-attachments/assets/d374508c-4146-41fa-af5c-1512efcdd7eb)

![Screenshot 4](https://github.com/user-attachments/assets/f5e2d863-30c9-4f01-ab07-f78f2fceda22)

![Screenshot 5](https://github.com/user-attachments/assets/8292cffd-9ec7-4004-add4-2d7da7063240)

![Screenshot 6](https://github.com/user-attachments/assets/66855a0e-e429-4ec0-a237-1cf45b12a74a)

### License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
