# J.A.R.V.I.S. — Assistente Pessoal por Voz

Assistente de voz ativado por palmas + frase de comando, com interface futurista estilo Jarvis do Homem de Ferro.

## Como Funciona

1. O sistema fica sempre ouvindo pelo microfone
2. Quando detecta **palmas** (2 batidas), entra em modo de escuta
3. Se ouvir **"acorda criança, vamos trabalhar"**, ativa o assistente
4. Jarvis responde com voz e a interface reage visualmente
5. Após silêncio, volta ao modo standby

## Requisitos

- macOS (usa o comando `say` para voz)
- Python 3.10+
- Homebrew
- Microfone
- Chave de API da Anthropic (Claude)

## Instalação

```bash
cd jarvis
chmod +x setup.sh
./setup.sh
```

## Uso

```bash
export ANTHROPIC_API_KEY='sua-chave-aqui'
source .venv/bin/activate
python main.py
```

O navegador abrirá automaticamente com a interface futurista.

## Configuração

Variáveis de ambiente opcionais:

| Variável | Padrão | Descrição |
|---|---|---|
| `ANTHROPIC_API_KEY` | (obrigatório) | Chave da API Claude |
| `JARVIS_MODEL` | `claude-sonnet-4-20250514` | Modelo Claude a usar |
| `JARVIS_VOICE` | `Luciana` | Voz do macOS (pt-BR) |
| `JARVIS_VOICE_RATE` | `180` | Velocidade da fala |
| `VOSK_MODEL_PATH` | `~/.jarvis/vosk-model-pt` | Caminho do modelo de fala |

## Arquitetura

```
jarvis/
├── main.py              # Ponto de entrada — orquestra tudo
├── core/
│   ├── clap_detector.py # Detecta palmas no áudio
│   ├── wake_phrase.py   # Reconhece a frase de ativação
│   ├── listener.py      # Pipeline de áudio contínuo
│   ├── speech_recognizer.py  # Speech-to-text (Vosk)
│   ├── brain.py         # Conversação IA (Claude API)
│   ├── voice.py         # Text-to-speech (macOS say)
│   └── server.py        # WebSocket server
├── frontend/
│   └── index.html       # Interface futurista com partículas
├── setup.sh             # Script de instalação
└── requirements.txt     # Dependências Python
```

## Vozes Disponíveis (macOS pt-BR)

Para listar vozes: `say -v '?'| grep pt`

- **Luciana** — Voz feminina (padrão)
- **Felipe** — Voz masculina
