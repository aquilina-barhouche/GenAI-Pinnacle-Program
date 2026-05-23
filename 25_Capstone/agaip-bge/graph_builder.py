import os
from typing import Optional

from sentence_transformers import SentenceTransformer
from rerankers import Reranker
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tools.base import BaseTool
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Checkpointer
from qdrant_client import QdrantClient

reranker = Reranker("BAAI/bge-reranker-v2-m3", model_type="cross-encoder")
class BGEEmbedding(Embeddings):
    def __init__(self):
        super().__init__()
        self.model = SentenceTransformer("BAAI/bge-m3")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()


def create_qdrant_search_tool() -> BaseTool:

    client = QdrantClient(
        url=os.environ["QDRANT_ENDPOINT"],
        api_key=os.environ["QDRANT_API_KEY"],
        timeout=60,
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=os.environ["COLLECTION"],
        content_payload_key="text",
        embedding=BGEEmbedding(),
        vector_name="dense",
        retrieval_mode=RetrievalMode.DENSE,
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"limit": 50},
    )

    @tool
    def search(augmented_query: str) -> str:
        """Search the database for information matching the query

        Args:
            augmented_query (str): The original or augmented query of the user.
        """

        docs = retriever.invoke(input=augmented_query)

        if docs:
            passages = [doc.page_content for doc in docs]

            results = reranker.rank(query=augmented_query, docs=passages)

            top_10 = [result.text for result in results.results[:10]]

            messages = "\n\n".join(top_10)

            return messages

        return f"No information can be found about: `{augmented_query}`."

    return search


def create_chatbot_graph(
    rag_system_prompt,
    checkpointer: Optional[Checkpointer] = None,
) -> CompiledStateGraph:

    rag_model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_ENDPOINT"],
        azure_deployment=os.environ["RAG_MODEL"],
        api_version="2025-01-01-preview",
        api_key=os.environ["AZURE_API_KEY"],  # type: ignore
    )

    search_tool = create_qdrant_search_tool()

    rag_agent = create_agent(
        rag_model,
        [search_tool],
        system_prompt=rag_system_prompt,
        checkpointer=checkpointer,
    )

    return rag_agent
