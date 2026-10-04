"""Ponto de entrada do projeto.

Uso web:  python main.py
Uso CLI:  python main.py --cli "Sua pergunta"
"""
import argparse

from app import MODELOS_GRATUITOS, MODELO_PADRAO, app
from core.request_model import perguntar


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", metavar="PERGUNTA", help="faz uma pergunta sem abrir a interface web")
    args = parser.parse_args()
    if args.cli:
        print(perguntar(MODELO_PADRAO, args.cli))
    else:
        print(f"Modelos disponíveis: {', '.join(MODELOS_GRATUITOS)}")
        app.run(host="127.0.0.1", port=5000, debug=False)
