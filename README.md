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

1. Start external ChromaDB

    ```shell
    podman build -t quay.io/foo/chroma -f ./chroma/ChromaContainerfile .
    podman run --rm --name chroma -p 8000:8000 -t quay.io/foo/chroma
    ```

2. Start App

    ```shell
    export OPENAI_API_KEY=sk-replaceme
    export APP_PASSWORD=replaceme
    export FLASK_SECRET_KEY=replacemealso
    export CHROMA_HOST=localhost
    export CHROMA_PORT=8000
    export OPENAPI_MODEL_NAME=text-embedding-ada-002
    export PORT=5000
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
