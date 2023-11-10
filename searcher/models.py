from langchain.embeddings import LlamaCppEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.llms import LlamaCpp
from chromadb import HttpClient, Documents, EmbeddingFunction, Embeddings
from chromadb.api.models.Collection import Collection
from openai.error import AuthenticationError, RateLimitError
from logging import getLogger
from searcher.extensions import db
from datetime import datetime
from chromadb.utils import embedding_functions
from huggingface_hub import login

class LlamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        # model_id = 'sentence-transformers/all-MiniLM-L6-v2'
        # model_kwargs = {'device': 'cpu'}
        # encode_kwargs = {'normalize_embeddings': False}
        # self._embedding_function = HuggingFaceEmbeddings(
            # model_name=model_id,
            # model_kwargs=model_kwargs,
        # )

        self._embedding_function = LlamaCppEmbeddings(
            model_path="./models/llama-2-7b.Q5_K_M.gguf",
            n_ctx=2048,
            n_batch=1024,
            n_threads=8
        )
    def embed_documents(self, texts):
        embeddings = self._embedding_function.embed_documents(texts)
        return embeddings
        # return [list(map(float, e)) for e in embeddings]
    def embed_query(self, text):
        embeddings = self._embedding_function.embed_query(text)
        return embeddings
        # return [list(map(float, e)) for e in embeddings][0]
    # def __call__(self, texts: Documents) -> Embeddings:
        # return embeddings.embed_documents(list(map(lambda t: t, texts.copy())))

class Fact(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    title = db.Column(db.String(256))
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<Fact "{self.title}">'

class TrainingError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class Searcher:
    def __init__(self, openai_api_key:str, open_ai_model_name:str, chroma_host:str, chroma_port:str):
        model_path = './models/vicuna-7b-v1.5.Q4_K_M.gguf'
        # model_path="./models/llama-2-7b.Q5_K_M.gguf"
        llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=1,
            n_batch=512,
            n_ctx=2048,
            verbose=True,
            n_threads=8,
            temperature=0.7,
            top_p=0.5,
            top_k=40,
            repeat_penalty=1.17647,
            last_n_tokens_size=256,
            max_tokens=1024
        )
        self._chain:BaseCombineDocumentsChain = load_qa_chain(llm, chain_type='stuff')
        self._dbclient = HttpClient(host=chroma_host, port=chroma_port)
        self._collection_name = "chroma"
        # TODO: replace
        # self._embedding_function = OpenAIEmbeddingFunction(
            # api_key=openai_api_key,
            # model_name=open_ai_model_name
        # )
        # login("hf_key")
        # self._embedding_function = embedding_functions.HuggingFaceEmbeddingFunction(
            # api_key="hf_key",
            # model_name="sentence-transformers/all-MiniLM-L6-v2"
        # )
        self._embedding_function = LlamaEmbeddingFunction()
        self._collection = self._dbclient.get_or_create_collection(name=self._collection_name)
        self._logger = getLogger(__name__)


    def train(self, values):
        """
        Train the model
        """
        doc_str = "\n\n".join(values)
        self._collection = self._generate_index(doc_str)


    def _generate_index(self, text:str) -> Collection:
        """
        Index the document and return the indexed db
        """
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        documents = text_splitter.split_text(text)

        self._dbclient.get_or_create_collection(name=self._collection_name)
        self._dbclient.delete_collection(name=self._collection_name)

        embedding_function = self._embedding_function
        collection = self._dbclient.create_collection(name=self._collection_name, embedding_function=embedding_function)
        try:
            collection.add(documents=documents, ids=list(map(lambda num: str(num), range(len(documents)))))
        except AuthenticationError as e:
            self._logger.error(e)
            raise TrainingError('Invalid OPENAI Key')
        except RateLimitError as e:
            self._logger.error(e)
            raise TrainingError('Rate Limit Error while using OPENAI Key')
        return collection


    def _answer_question(self, query:str, chain:BaseCombineDocumentsChain) -> str:
        """
        Takes in query, index to search from, and llm chain to generate answer
        """
        embedding_function = self._embedding_function
        query_db = Chroma(client=self._dbclient, collection_name=self._collection_name, embedding_function=embedding_function)

        num_query = query_db._collection.count()
        docs = query_db.similarity_search_by_vector(embedding_function.embed_query(query), num_query)
        answer:dict[str, str] = chain({'input_documents': docs, 'question': query}, return_only_outputs=True)
        return answer['output_text']


    def ask(self, query:str) -> str:
        """
        Ask the model a query
        """
        return self._answer_question(query, self._chain)
