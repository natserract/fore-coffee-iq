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

Database setup:

1. Create a new API key in the [Pinecone](https://www.pinecone.io/) console, or use the connect widget below to generate a key.
2. Copy your generated key:
```bash
PINECONE_API_KEY="YOUR_API_KEY"
```
3. Create an index on console
4. Copy your index host:
```bash
PINECONE_INDEX_HOST="YOUR_INDEX_HOST'
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
