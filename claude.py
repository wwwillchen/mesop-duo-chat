import anthropic
from typing import Iterable

from data_model import ChatMessage, State
import mesop as me

def call_claude_sonnet(input: str, history: list[ChatMessage]) -> Iterable[str]:
    state = me.state(State)
    client = anthropic.Anthropic(api_key=state.claude_api_key)
    messages = [
        {
            "role": "assistant" if message.role == "model" else message.role,
            "content": message.content,
        }
        for message in history
    ] + [{"role": "user", "content": input}]

    with client.messages.stream(
        max_tokens=1024,
        messages=messages,
        model="claude-3-sonnet-20240229",
    ) as stream:
        for text in stream.text_stream:
            yield text
