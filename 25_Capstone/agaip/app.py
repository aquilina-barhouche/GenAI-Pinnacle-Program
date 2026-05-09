from typing import TYPE_CHECKING, cast
from uuid import uuid4

import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver

from graph_builder import create_chatbot_graph
from system_prompts import RAG_AGENT_PROMPT

if TYPE_CHECKING:
    from langchain_core.runnables.config import RunnableConfig


# Set page config
st.set_page_config(layout="wide", page_title="SABIS® GENIUS", page_icon="✨")


def create_thread_id() -> str:

    return str(uuid4())


# Initialize Session
if "chatbot_graph" not in st.session_state:

    memory = InMemorySaver()

    chatbot_graph = create_chatbot_graph(RAG_AGENT_PROMPT, memory)

    st.session_state.chatbot_graph = chatbot_graph


# Initialize thread_id
if "thread_id" not in st.session_state:
    st.session_state.thread_id = create_thread_id()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SABIS® GENIUS")
with st.expander("Session ID Info"):
    st.markdown(f"Session started with ID: `{st.session_state.thread_id}`.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if query := st.chat_input("Say something"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(query)
    # st.session_state.chain.stream({"input": "What is a cell?"})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream_placeholder = st.empty()

        config = cast(
            "RunnableConfig",
            {"configurable": {"thread_id": st.session_state.thread_id}},
        )

        stream_text = ""

        try:

            for chunk in st.session_state.chatbot_graph.stream(
                input={"messages": st.session_state.messages},
                config=config,
                stream_mode="updates",
            ):
                if chunk.get("model"):
                    stream_text += chunk["model"]["messages"][0].content
                    stream_placeholder.markdown(stream_text)

            stream_placeholder.empty()  # clean-up the placeholder

        except Exception as err:
            stream_placeholder.error("Something went wrong! Try again.")
            print(err)

        st.markdown(stream_text)

    st.session_state.messages.append({"role": "assistant", "content": stream_text})
