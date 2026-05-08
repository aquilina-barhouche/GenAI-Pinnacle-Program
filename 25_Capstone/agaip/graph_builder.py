import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tools.base import BaseTool
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Checkpointer
from qdrant_client import QdrantClient


def create_qdrant_search_tool() -> BaseTool:

    client = QdrantClient(
        url=os.environ["QDRANT_ENDPOINT"],
        api_key=os.environ["QDRANT_API_KEY"],
        timeout=60,
    )

    embedding = AzureOpenAIEmbeddings(
        azure_endpoint=os.environ["AZURE_ENDPOINT"],
        model=os.environ["EMBEDDING_MODEL"],
        api_version="2024-12-01-preview",
        api_key=os.environ["AZURE_API_KEY"],  # type: ignore
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=os.environ["COLLECTION"],
        embedding=embedding,
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
    )

    @tool
    def search(augmented_query: str) -> str:
        """Search the database for information matching the query

        Args:
            augmented_query (str): The original or augmented query of the user.
        """

        docs = retriever.invoke(input=augmented_query)

        if docs:
            messages = "\n\n".join([doc.page_content for doc in docs])

            return messages

        return f"No information can be found about: `{augmented_query}`."

    return search


def create_chatbot_graph(
    rag_system_prompt,
    checkpointer: Checkpointer,
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
