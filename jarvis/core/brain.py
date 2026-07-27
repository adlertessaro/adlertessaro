import os

import anthropic


SYSTEM_PROMPT = """Você é Jarvis, um assistente pessoal inteligente e sofisticado.
Seu criador é o Adler. Você fala em português brasileiro.
Você é espirituoso, eficiente e direto. Suas respostas são concisas mas úteis.
Quando ativado, você cumprimenta brevemente e pergunta como pode ajudar.
Mantenha respostas curtas — no máximo 2-3 frases — a menos que peçam detalhes.
Você tem personalidade: é confiante, levemente sarcástico de forma amigável,
e sempre prestativo. Pense no Jarvis do Homem de Ferro como inspiração."""


class Brain:
    """AI conversation engine powered by Claude."""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Export it before running Jarvis."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation = []
        self.model = os.environ.get("JARVIS_MODEL", "claude-sonnet-4-20250514")

    def greet(self) -> str:
        self.conversation = []
        return self.chat("O usuário acabou de me ativar com o comando de voz. Cumprimente brevemente.")

    def chat(self, user_text: str) -> str:
        self.conversation.append({"role": "user", "content": user_text})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=self.conversation,
        )

        reply = response.content[0].text
        self.conversation.append({"role": "assistant", "content": reply})

        if len(self.conversation) > 20:
            self.conversation = self.conversation[-20:]

        return reply

    def reset(self):
        self.conversation = []
