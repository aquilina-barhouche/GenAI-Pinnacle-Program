from uuid import uuid4

import streamlit as st

from db.sqlite_memory import SQLiteMemory
from graph_builder import create_chatbot_graph
from system_prompts import RAG_AGENT_PROMPT

# Set page config
st.set_page_config(layout="wide", page_title="GenAI Pinnacle Chatbot", page_icon="✨")

sqlite_memory = SQLiteMemory("./db/conversations.db")


def create_thread_id() -> str:
    return str(uuid4())


def login_page():
    st.sidebar.subheader("Profile")
    if st.sidebar.button(
        "Log in with Google", type="primary", icon=":material/account_circle:"
    ):
        st.login("google")
    st.sidebar.divider()
    st.warning("Please log in to use the app.", icon=":material/lock:")


if not st.user.get("is_logged_in"):
    login_page()
    st.stop()


# Initialize Session
if "chatbot_graph" not in st.session_state:
    chatbot_graph = create_chatbot_graph(RAG_AGENT_PROMPT)
    st.session_state.chatbot_graph = chatbot_graph

# Initialize thread_id
if "thread_id" not in st.session_state:
    st.session_state.thread_id = create_thread_id()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


st.sidebar.subheader("Profile")
st.sidebar.write(f"Welcome, {st.user.name}!")
st.sidebar.image(st.user.picture, width=50)  # type: ignore

if st.sidebar.button("Log out", type="primary", icon=":material/account_circle:"):
    st.logout()

st.sidebar.subheader("History")

if st.user.get("is_logged_in"):
    user_sessions = sqlite_memory.get_user_sessions(st.user.sub)  # type: ignore
else:
    st.stop()


def reload_session(uuid):
    st.session_state.thread_id = uuid
    st.session_state.messages = sqlite_memory.get_messages(uuid)


def stylize_text(text: str) -> str:
    if len(text) > 23:
        return text[0:21] + "..."
    return text


with st.sidebar.container(border=True, height=300):
    for uuid, text in user_sessions:
        if st.button(stylize_text(text), key=uuid, use_container_width=True):
            reload_session(uuid)


with st.container(border=True):
    left, right = st.columns([3, 5], gap="xxsmall", vertical_alignment="center")
    left.markdown(
        '<p style="font-size: 36px;">GenAI Pinnacle Chatbot</p>', unsafe_allow_html=True
    )
    if right.button(
        "Start New Chat",
        type="tertiary",
        icon=":material/add_comment:",
        use_container_width=False,
    ):
        st.session_state.thread_id = create_thread_id()
        st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if query := st.chat_input("Say something"):
    # Add user message to chat history
    sqlite_memory.insert_session_id(st.session_state.thread_id, st.user.sub, query)  # type: ignore
    user_message = {"role": "user", "content": query}
    sqlite_memory.append_message(st.session_state.thread_id, user_message)
    st.session_state.messages.append(user_message)

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(query)
    # st.session_state.chain.stream({"input": "What is a cell?"})
    # Display assistant response in chat message container
    with st.spinner(show_time=True), st.chat_message("assistant"):
        stream_placeholder = st.empty()

        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        stream_text = ""

        try:
            for chunk in st.session_state.chatbot_graph.stream(
                input={"messages": st.session_state.messages},
                config=config,  # type: ignore
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

    assistant_message = {"role": "assistant", "content": stream_text}
    sqlite_memory.append_message(st.session_state.thread_id, assistant_message)
    st.session_state.messages.append(assistant_message)
