# Semantic Searcher

## Prerequisite

1. Python 3.10

## Setup

1. Install deps

    ```shell
    # pip install langchain openai chromadb unstructured evaluate bert_score tiktoken
    pip install -r requirements.txt
    ```

2. Set `OPENAI_API_KEY` and `APP_PASSWORD` and `FLASK_SECRET_KEY` and `CHROMA_HOST`, and `CHROMA_PORT`, and optionally `PORT` and `OPENAPI_MODEL_NAME` env vars

    ```shell
    # use this for your FLASK_SECRET_KEY
    python -c 'import secrets; print(secrets.token_hex())'
    ```

## Running

```shell
# remember to export `OPENAI_API_KEY` and `APP_PASSWORD` and `FLASK_SECRET_KEY` and `CHROMA_HOST`, and `CHROMA_PORT` as env vars
flask --app searcher
```

## Deployment

```shell
# update `env` in `kube/app.yaml`
oc apply -k ./kube
```


## Links

1. [Inspired by this](https://github.com/redhat-et/foundation-models-for-documentation/blob/master/notebooks/langchain-openai.ipynb)
2. [Chroma DB](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html)
