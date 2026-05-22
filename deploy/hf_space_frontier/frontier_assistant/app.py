"""Gradio UI for the Frontier assistant."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gradio as gr

from frontier_assistant.assistant import FrontierAssistant
from shared.gradio_chat import create_chatbot, format_for_gradio, normalize_history

assistant = FrontierAssistant()


def respond(message: str, history: list):
    if not message.strip():
        return "", history or []
    _, updated = assistant.chat(message, normalize_history(history))
    return "", format_for_gradio(updated)


def clear_history():
    return []


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Frontier Personal Assistant") as demo:
        gr.Markdown(
            """
            # Frontier Personal Assistant
            **Provider:** Groq (`llama-3.3-70b-versatile` by default)  
            Same system prompt, memory, and guardrails as the OSS assistant for fair comparison.
            """
        )
        chatbot = create_chatbot(label="Conversation", height=420)
        msg = gr.Textbox(label="Your message", placeholder="Ask me anything...")
        with gr.Row():
            send = gr.Button("Send", variant="primary")
            clear = gr.Button("Clear history")

        send.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(clear_history, None, chatbot)

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7861)
