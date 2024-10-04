# Simple Retrieval-Augmented Generation (RAG) Chatbot

The retrieval-augmented generation (RAG) enables retrieval of relevant information from an external knowledge source and allows large language models (LLMs) to answer queries over previously unseen document collections.

## Setups

```bash
cp .env.example .env

# Managing environments
pyenv install 3.11
pyenv local 3.11  # Activate Python 3.11 for the current project

# Activate environment
python3 -m venv .venv
source .venv/bin/activate
```

To install dependencies:

```bash
make install
```

## Running
```bash
make run
```

On development mode:
```bash
make dev
```
