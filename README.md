# PyLaama AI Chat

**PyLaama AI Chat** is an interactive **chat interface** built with [Streamlit](https://streamlit.io/), designed to harness the power of Large Language Models (LLMs) for AI-driven conversations. The application leverages [Ollama](https://ollama.ai/) to run various LLM models locally, with default support for [Meta Llama 3.1 8B](https://llama.meta.com/) *(default model)* and [Google Gemma 2 9B](https://ai.google.dev/gemma) models to provide intelligent, context-aware responses.

## Features

- 🤖 **Interactive AI Chat**: Chat interface for dynamic conversations with sophisticated AI models
- 🔄 **Model Flexibility**: Easily switch between different LLM models supported by Ollama
- 📄 **Document Context**: Document upload support to provide additional context for more informed AI responses
- 💾 **Session Management**: Save, load, and manage multiple chat sessions for continuity and reference (SQLite or PostgreSQL)
- 👤 **Multi-User Support**: Basic authentication system allowing multiple users to maintain separate chat histories and preferences
- 🎨 **User-Friendly Interface**: Custom-styled Streamlit-powered UI for interaction

**PyLaama AI Chat** combines cutting-edge AI technology with practical features, making it ideal for **learning, and exploration** in the realm of Artificial Intelligence and Natural Language Processing (NLP).

## Installation

### Prerequisites

- Python
- Ollama
- *Optional: PostgreSQL (default: SQLite)*

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

PyLaama AI Chat uses Ollama to run LLM models locally. By default, it supports Llama 3.1 and Gemma 2, but you can easily add support for any model available in Ollama:

1. Pull the desired model using Ollama:

```
ollama pull model_name
```

2. Add the model name to the list of available models in `laama_chat.py`.

For a list of available models and their capabilities, visit [Ollama's model library](https://ollama.ai/library).

## Project Structure

```
laama_chat /
├── .streamlit/
│   └── config.toml
├── auth/
│   └── config.yaml
├── css/
│   └── styles.css
├── files/
│   └── bg_image.png
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


### License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
