from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader

class Searcher:
    def __init__(self, openai_api_key):
        openai = OpenAI(temperature=0, openai_api_key=openai_api_key)
        self._chain = load_qa_chain(openai, chain_type='stuff')
        self._docsearch = None


    def train(self, posts):
        """
        Train the model
        """
        doc_str = "\n\n".join(list(map(lambda p: p['body'], posts)))

        # write string
        filename = '/tmp/data.txt'
        with open(filename, 'w') as f:
            f.write(doc_str)
        self._docsearch = self._generate_index(filename)


    def _generate_index(self, path:str) -> Chroma:
        """
        Index the document and return the indexed db
        """

        # chromadb
        loader = TextLoader(path)
        # loader = DirectoryLoader('../data/external', glob="**/*.md", loader_cls=TextLoader)
        documents = loader.load()

        text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()

        # persist
        # docsearch = Chroma.from_documents(texts, embeddings, persist_directory='../data/interim')
        #docsearch.persist()

        # don't persist
        return Chroma.from_documents(texts, embeddings)


    def _answer_question(self, query:str, index:Chroma, chain) -> str:
        """
        Takes in query, index to search from, and llm chain to generate answer
        """
        ## Retrieve docs
        docs = index.similarity_search(query)
        # print(docs[0].page_content)  # get content

        # return answer
        # return chain.run(input_documents=docs, question=query)

        # get back model and return output text
        answer = chain({'input_documents': docs, 'question': query}, return_only_outputs=True)
        return answer['output_text']


    def ask(self, query:str) -> str:
        """
        Ask the model a query
        """

        if self._docsearch is None:
            return 'You must train the model first. Go back to the content page and train.'
        else:
            return self._answer_question(query, self._docsearch, self._chain)
