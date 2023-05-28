# Semantic Searcher

## Prerequisite

1. Python 3.11

## Setup

1. Install deps

    ```shell
    # pip install langchain openai chromadb unstructured evaluate bert_score tiktoken
    pip install -r requirements.txt
    ```

2. Set `OPENAI_API_KEY` and `APP_PASSWORD` env var

## Running

```shell
flask --app searcher
```
