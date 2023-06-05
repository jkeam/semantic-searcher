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

## Deployment

1. Update `env` in `kube/app.yaml`
2. Update ingress/route in `kube/app.yaml` to match your specific environment
3. Deploy using a kubernetes environment


## Links

1. [Inspired by this](https://github.com/redhat-et/foundation-models-for-documentation/blob/master/notebooks/langchain-openai.ipynb)
2. [Chroma DB](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html)
