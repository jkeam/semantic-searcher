from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from shutil import rmtree
from chromadb import HttpClient
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

class Searcher:
    def __init__(self, openai_api_key:str, open_ai_model_name:str, chroma_host:str, chroma_port:int):
        openai:OpenAI = OpenAI(temperature=0, openai_api_key=openai_api_key)
        self._chain:BaseCombineDocumentsChain = load_qa_chain(openai, chain_type='stuff')
        self._dbclient = HttpClient(host=chroma_host, port=chroma_port)
        self._collection:Collection|None = None
        self._collection_name = "chroma"
        self._embedding_function = OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name=open_ai_model_name
        )


    def train(self, posts):
        """
        Train the model
        """
        doc_str = "\n\n".join(list(map(lambda p: p['body'], posts)))
        self._collection = self._generate_index(doc_str)


    def _generate_index(self, text:str) -> Collection:
        """
        Index the document and return the indexed db
        """
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        documents = text_splitter.split_text(text)

        self._dbclient.delete_collection(name=self._collection_name)
        collection = self._dbclient.create_collection(name=self._collection_name, embedding_function=self._embedding_function)
        collection.add(documents=documents, ids=list(map(lambda num: str(num), range(len(documents)))))
        return collection


    def _answer_question(self, query:str, collection:Collection, chain:BaseCombineDocumentsChain) -> str:
        """
        Takes in query, index to search from, and llm chain to generate answer
        """
        query_db = Chroma(client=self._dbclient, collection_name=self._collection_name, embedding_function=OpenAIEmbeddings())
        docs = query_db.similarity_search(query)
        answer:dict[str, str] = chain({'input_documents': docs, 'question': query}, return_only_outputs=True)
        return answer['output_text']


    def ask(self, query:str) -> str:
        """
        Ask the model a query
        """
        if self._collection is None:
            return 'You must train the model first. Go back to the content page and train.'
        else:
            return self._answer_question(query, self._collection, self._chain)
