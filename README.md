# Semantic Searcher

## Local Setup

### Prerequisite

1. Python 3.10

### Setup

1. Install deps

    ```shell
    # pip install langchain openai chromadb unstructured evaluate bert_score tiktoken
    pip install -r requirements.txt
    ```

2. Set `OPENAI_API_KEY` and `APP_PASSWORD` and `FLASK_SECRET_KEY` and `CHROMA_HOST`, and `CHROMA_PORT`, and optionally `PORT` and `OPENAPI_MODEL_NAME` and `DB_USER` and `DB_PASSWORD` and `DB_DATABASE` env vars

    ```shell
    # use this for your FLASK_SECRET_KEY
    python -c 'import secrets; print(secrets.token_hex())'
    ```

### Running

1. Start external ChromaDB

    ```shell
    podman build -t chroma -f ./chroma/ChromaContainerfile .
    podman run --rm --name chroma -p 8000:8000 -t chroma
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

1. Update `./kube/env.txt`, really only `OPENAI_API_KEY` MUST be updated

2. Create an OpenShift project/namespace.  Project name is up to you, but you will have change the `kustomization.yaml` if you use a different namespace than `semantic-searcher`.

    ```shell
    oc new-project semantic-searcher
    ```

3. Optionally, if you changed the project name, then update the following in `kustomization.yaml`:

    ```yaml
    namespace: <replace with new project name>
    ...
    configMapGenerator:
    - name: chromaprops
      literals:
      - CHROMA_HOST=semantic-searcher-chroma.<replace with new project name>.svc.cluster.local
    ```

4.  Run everything

    ```shell
    oc apply -k ./kube
    ```

5.  Open the URL for the `semantic-searcher-app` and log in with username `admin` and `APP_PASSWORD` password that you set in `env.txt`


## Links

1. [Inspired by this](https://github.com/redhat-et/foundation-models-for-documentation/blob/master/notebooks/langchain-openai.ipynb)
2. [Chroma DB](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html)
