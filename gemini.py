import google.generativeai as genai
from typing import Iterable

from data_model import ChatMessage, State
import mesop as me

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

def configure_gemini():
    state = me.state(State)
    genai.configure(api_key=state.gemini_api_key)

def send_prompt_pro(prompt: str, history: list[ChatMessage]) -> Iterable[str]:
    configure_gemini()
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=[
            {"role": message.role, "parts": [message.content]} for message in history
        ]
    )
    for chunk in chat_session.send_message(prompt, stream=True):
        yield chunk.text

def send_prompt_flash(prompt: str, history: list[ChatMessage]) -> Iterable[str]:
    configure_gemini()
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=[
            {"role": message.role, "parts": [message.content]} for message in history
        ]
    )
    for chunk in chat_session.send_message(prompt, stream=True):
        yield chunk.text
