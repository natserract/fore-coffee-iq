import config
import logging
import langchain_pinecone as lp
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from tqdm.auto import tqdm

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

    def create_embeddings(
        self,
        data: list[dict]
    ):
        is_exist = False
        for ids in self.index.list():
            if len(ids) > 0:
                is_exist = True
                break;

        if is_exist == True:
            logger.info('Resetting existing data')
            self.index.delete(delete_all=True)
            self.save_embeddings(data)
        else:
            logger.info(f'Create new data')
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
            doc = Document(page_content=content, metadata={"id": item["id"]})
            docs.append(doc)

        # Upsert to pinecone
        self._vector_store.add_documents(documents=docs)
