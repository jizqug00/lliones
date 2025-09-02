import gradio as gr
from llama_cpp import Llama
import os

# ---------------- Configuración ----------------
MODEL_REPOS = {
    "0.5B": "unileon-robotics/Trasgu-0.5B-GGUF",
    "1.5B": "unileon-robotics/Trasgu-1.5B-GGUF",
    "3B": "unileon-robotics/Trasgu-3B-GGUF",
}
QUANTIZATION_FILES = {
    "F16": "unsloth.F16.gguf",
    "Q5":  "unsloth.Q5_K_M.gguf",
}

_loaded = {}

def load_model(size: str, quant: str) -> Llama:
    key = (size, quant)
    if key not in _loaded:
        repo_id = MODEL_REPOS[size]
        filename = QUANTIZATION_FILES[quant]
        print(f"🔄 Cargando modelo {repo_id}/{filename} ...")

        _loaded[key] = Llama.from_pretrained(
            repo_id=repo_id,
            filename=filename,
            chat_format="qwen",
            n_ctx=4096,
            n_threads=os.cpu_count() or 4,
            n_gpu_layers=-1,
            verbose=False,
        )
    return _loaded[key]

# ===== SIN HISTORIAL (para el modelo), PERO ACUMULANDO EN UI =====
def generate(user_message, history, size, quant, temperature, max_new_tokens, system_prompt):
    llm = load_model(size, quant)

    # El modelo solo ve system + user (sin historial):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    partial = ""
    for chunk in llm.create_chat_completion(
        messages=messages,
        temperature=float(temperature),
        max_tokens=int(max_new_tokens),
        stream=True,
    ):
        delta = chunk["choices"][0]["delta"].get("content") or ""
        if delta:
            partial += delta
            # En la UI, sí acumulamos las rondas previas:
            yield history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": partial},
            ]

def clear_box():
    return ""

# ---------------- Interfaz (sin CSS) ----------------
with gr.Blocks() as demo:
    with gr.Row():
        # Columna izquierda (logo arriba, luego sidebar)
        with gr.Column(scale=1, min_width=280):
            gr.Image("Imágenes/Logo-Trasgu.png", show_label=False)

            # Barra lateral con controles
            with gr.Group():
                gr.Markdown("<h3 style='margin: .25rem 0 .5rem 45px;'>Configuración recomendada</h3>")
                size = gr.Radio(
                    ["3B", "1.5B", "0.5B"], value="3B",
                    label="Tamaño del modelo"
                )
                quant = gr.Radio(
                    ["F16","Q5"], value="F16",
                    label="Cuantización"
                )
                temperature = gr.Slider(
                    minimum=0.1, maximum=2.0, value=0.7, step=0.1,
                    label="Temperatura"
                )
                max_tokens = gr.Slider(
                    minimum=64, maximum=4096, value=512, step=64,
                    label="Max new tokens"
                )

        # Columna derecha (chat y system prompt en acordeón)
        with gr.Column(scale=4, min_width=600):
            chatbot = gr.Chatbot(type="messages", height=520)
            with gr.Row():
                msg = gr.Textbox(placeholder="Escribe aquí…", scale=5, show_label=False)
                send = gr.Button("Enviar", variant="primary", scale=1)

            with gr.Accordion("System prompt", open=False):
                system_prompt = gr.Textbox(
                    value="Eres Trasgu, un Diccionario/Traductor experto en leonés.",
                    lines=3,
                    show_label=False,
                )

            # Eventos: generar y limpiar caja (SIN resetear el chat)
            msg.submit(
                generate,
                [msg, chatbot, size, quant, temperature, max_tokens, system_prompt],
                [chatbot],
            ).then(clear_box, outputs=[msg])

            send.click(
                generate,
                [msg, chatbot, size, quant, temperature, max_tokens, system_prompt],
                [chatbot],
            ).then(clear_box, outputs=[msg])

if __name__ == "__main__":
    demo.launch()