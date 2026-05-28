import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ler_folha_manual_ia(caminho_imagem):
    with open(caminho_imagem, "rb") as arquivo:
        imagem_bytes = arquivo.read()

    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=imagem_bytes,
                mime_type="image/jpeg"
            ),
            """
Leia esta folha ponto manual e extraia os horários.

Retorne APENAS em JSON neste formato:

[
  {
    "dia": 1,
    "entrada": "07:30",
    "saida_almoco": "11:45",
    "volta_almoco": "13:15",
    "saida_final": "18:00"
  }
]

Se algum horário estiver ilegível, use null.
"""
        ]
    )

    texto = resposta.text.strip()

    texto = texto.replace("```json", "")
    texto = texto.replace("```", "")
    texto = texto.strip()

    dados = json.loads(texto)

    return dados