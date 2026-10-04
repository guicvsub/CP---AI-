import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

from core.request_model import OpenRouterError, conversar

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder="frontend", static_url_path="/static")

MODELOS_GRATUITOS = {
    "qwen_chat": "qwen/qwen3.8-27b:free",
    "gemma_multimodal": "google/gemma-4-31b-it:free",
    "cohere_codigo": "cohere/north-mini-code:free",
    "nemotron_contexto_longo": "nvidia/nemotron-3.5-lightning:free",
    "roteador_gratuito": "openrouter/free",
}
MODELO_PADRAO = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")


@app.get("/")
def index():
    return send_from_directory(BASE_DIR / "frontend", "index.html")


@app.get("/api/config")
def config():
    return jsonify({
        "models": MODELOS_GRATUITOS,
        "default_model": MODELO_PADRAO,
        "history_policy": {
            "active": "summarize_old",
            "limit": 12,
            "alternatives": ["recent_messages", "new_session"],
        },
    })


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    messages = body.get("messages")
    model = body.get("model") or MODELO_PADRAO
    model = MODELOS_LEGADOS.get(model, model)

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "Envie pelo menos uma mensagem."}), 400
    if not all(isinstance(item, dict) for item in messages):
        return jsonify({"error": "Formato de histórico inválido."}), 400

    try:
        answer, sent_messages = conversar(
            model=model,
            messages=messages,
            strategy="summarize_old",
            max_messages=12,
        )
        return jsonify({
            "answer": answer,
            "sent_messages": len(sent_messages),
            "strategy": "summarize_old",
        })
    except OpenRouterError as exc:
        return jsonify({"error": str(exc), "kind": exc.kind}), exc.status_code
    except Exception:
        app.logger.exception("Falha inesperada ao conversar com o OpenRouter")
        return jsonify({
            "error": "Não foi possível concluir a conversa. Verifique a rede e tente novamente.",
            "kind": "network",
        }), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
if MODELO_PADRAO == "qwen/qwen3-4b:free":
    MODELO_PADRAO = "nvidia/nemotron-3.5-lightning:free"
MODELOS_LEGADOS = {
    "qwen/qwen3-4b:free": "nvidia/nemotron-3.5-lightning:free",
    "cohere/command-r7b-arabic:free": "cohere/north-mini-code:free",
    "google/gemma-3-27b-it:free": "google/gemma-4-31b-it:free",
    "nvidia/nemotron-nano-9b-v2:free": "nvidia/nemotron-3.5-lightning:free",
}
