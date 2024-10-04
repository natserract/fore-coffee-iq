import config
import logging
import uuid
import langchain_pinecone as lp
from pinecone import Pinecone
from tqdm.auto import tqdm
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from utils.clean_processor import CleanProcessor

logger = logging.getLogger(__name__)

class PineconeVectorStore:
    def __init__(
        self,
        model: str = 'text-embedding-ada-002',
    ) -> None:
        self.client = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index = self.client.Index(host=config.PINECONE_INDEX_HOST)
        self.embeddings = OpenAIEmbeddings(
            model=model,
        )
        self._vector_store = lp.PineconeVectorStore(index=self.index, embedding=self.embeddings)

    @property
    def vector_store(self):
        return self._vector_store

    @property
    def retriever(self):
        if self.vector_store:
            return self.vector_store.as_retriever()
        else:
            raise ValueError("No vector store provided")

    def create_embeddings(
        self,
        data: list[dict]
    ):
        is_exist = False
        for ids in self.index.list():
            if len(ids) > 0:
                is_exist = True
                break;

        if is_exist == False:
            logger.info(f'Create new data')
            # self.index.delete(delete_all=True) # if you want to reset all existing data
            self.save_embeddings(data)

    def save_embeddings(
        self,
        data: list[dict]
    ):
        docs: list[Document] = []
        for item in tqdm(data, desc="Create document embeddings"):
            content = item["context"] + " " + item["question"]
            if item["answers"]["text"]:
                content += " " + " ".join(item["answers"]["text"])
            doc = Document(page_content=content, metadata={
                "intent": item["intent"],
            })
            docs.append(doc)

        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=0, length_function=len
        )

        # Split the text documents into nodes.
        all_documents: list[Document] = []
        for doc in tqdm(docs, desc="Split the text documents into nodes"):
            # document clean
            document_text = CleanProcessor.clean(doc.page_content)
            doc.page_content = document_text

            # parse document to nodes
            document_nodes = text_splitter.split_documents([doc])
            split_documents: list[Document] = []
            for document_node in document_nodes:
                doc_id = str(uuid.uuid4())
                document_node.metadata["doc_id"] = doc_id
                page_content = document_node.page_content
                if page_content.startswith(".") or page_content.startswith("。"):
                    page_content = page_content[1:].strip()
                else:
                    page_content = page_content
                if len(page_content) > 0:
                    document_node.page_content = page_content
                    split_documents.append(document_node)

            all_documents.extend(split_documents)

            # Upsert to pinecone
            self._vector_store.add_documents(documents=all_documents)

    def fetch(self, query: str):
        results = self._vector_store.similarity_search_with_score(
            query, k=3
        )
        for res, score in results:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")
        return results
