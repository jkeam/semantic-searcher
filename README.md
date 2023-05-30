# Semantic Searcher

## Prerequisite

1. Python 3.10

## Setup

1. Install deps

    ```shell
    # pip install langchain openai chromadb unstructured evaluate bert_score tiktoken
    pip install -r requirements.txt
    ```

2. Set `OPENAI_API_KEY` and `APP_PASSWORD` and `FLASK_SECRET_KEY` and optionally `PORT` env vars

    ```shell
    # use this for your FLASK_SECRET_KEY
    python -c 'import secrets; print(secrets.token_hex())'
    ```

## Running

```shell
flask --app searcher
```
