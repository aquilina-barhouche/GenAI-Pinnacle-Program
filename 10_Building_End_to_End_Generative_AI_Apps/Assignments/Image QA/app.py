import base64

import streamlit as st
from openai import OpenAI

model = "gpt-4.1-mini"
subscription_key = "[replace with you own openai api key]"

client = OpenAI(
    api_key=subscription_key,
)

st.set_page_config(page_title="Visual QA Bot", page_icon="🤖", layout="centered")

st.title("🤖 Visual QA Bot")

st.text("🖼️ Visual QA Bot with Multimodal LLMs")

st.header("🔮 Generate image to text responses")

user_prompt = st.text_input(
    "Ask any question about the image",
    placeholder="Example: Describe the scene, objects, activities, mood…",
)

uploaded_file = st.file_uploader(
    "Choose an image", accept_multiple_files=False, type=["jpg", "jpeg", "png"]
)


def image_to_b64(img: bytes, fmt: str) -> str:
    b64 = base64.b64encode(img).decode("utf-8")
    b64 = f"data:{fmt};base64,{b64}"
    return b64


if uploaded_file:
    img_bytes = uploaded_file.read()
    mime_type = uploaded_file.type
    b64_img_data = image_to_b64(img_bytes, mime_type)
    st.image(uploaded_file)

generate_button = st.button("Generate Response")

st.header("AI Response")

if generate_button:
    if (not user_prompt) and (not uploaded_file):
        st.error("Question and Image are missing!")
    if (not user_prompt) and uploaded_file:
        st.error("Question is missing!")
    if not uploaded_file and user_prompt:
        st.error("Image is missing!")
    if user_prompt and uploaded_file:
        response = client.responses.create(
            input=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant tasked with answering user questions on the given image.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_prompt.strip()},
                        {
                            "type": "input_image",
                            "image_url": b64_img_data,
                        },
                    ],
                },  # type: ignore
            ],
            model=model,
        )

        st.markdown(response.output_text)
