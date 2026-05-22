"""Gradio UI for the OSS assistant."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gradio as gr

from oss_assistant.assistant import OSSAssistant
from shared.gradio_chat import create_chatbot, format_for_gradio, normalize_history

assistant = OSSAssistant()


def respond(message: str, history: list):
    if not message.strip():
        return "", history or []
    _, updated = assistant.chat(message, normalize_history(history))
    return "", format_for_gradio(updated)


def clear_history():
    return []


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="OSS Personal Assistant (Qwen2.5)") as demo:
        gr.Markdown(
            """
            # Open-Source Personal Assistant
            **Model:** Qwen2.5-0.5B-Instruct (Hugging Face)  
            Multi-turn memory · Input guardrails · Interaction logging
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
    demo.launch(server_name="0.0.0.0", server_port=7860)
