# OpenChat Study — cliente web para OpenRouter

Frontend em **HTML, CSS e JavaScript** integrado ao backend Python existente. A interface permite selecionar um modelo, enviar mensagens, visualizar a conversa e iniciar uma nova sessão.

> O projeto anterior era um cliente de terminal que usava `API_KEY`. A compatibilidade foi mantida, mas a variável recomendada e documentada para a entrega é `OPENROUTER_API_KEY`.

## Requisitos

- Python 3.10 ou superior
- Uma chave do [OpenRouter](https://openrouter.ai/keys)
- Um modelo disponível na conta. A lista inicial da tela usa modelos marcados como gratuitos no catálogo; confirme o catálogo da aula antes da apresentação, pois modelos gratuitos podem mudar.

## Instalação

No diretório deste projeto:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
```

Abra `.env` e preencha:

```env
OPENROUTER_API_KEY=sua_chave_aqui
OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free
```

A chave é lida em tempo de execução, não é enviada ao navegador e não é salva pelo frontend. O arquivo `.env` está no `.gitignore`.

## Executar

```bash
python main.py
```

Acesse <http://127.0.0.1:5000>.

Também é possível manter o modo de terminal do projeto anterior:

```bash
python main.py --cli "Qual é o sentido da vida?"
```

## Fluxo técnico

1. O navegador mantém a conversa somente em memória.
2. `POST /api/chat` recebe `model` e `messages`.
3. `core/request_model.py` usa uma única `requests.Session` reutilizável.
4. O backend resume o histórico antigo quando a conversa ultrapassa o limite e envia o resumo junto das últimas mensagens para `https://openrouter.ai/api/v1/chat/completions`.
5. A resposta é devolvida ao frontend e exibida como uma nova mensagem do assistente.

Endpoints:

- `GET /` — interface web.
- `GET /api/config` — modelos e política de contexto.
- `POST /api/chat` — conversa com o modelo.

## Estratégias de histórico

A estratégia ativa é `summarize_old`: quando há mais de 12 mensagens não-sistema, o backend faz uma chamada adicional ao mesmo modelo para resumir as mensagens antigas. No pedido principal, preserva uma mensagem `system`, adiciona o resumo e envia as últimas 12 mensagens não-sistema. Se a conversa ainda não ultrapassou o limite, não faz a chamada de resumo.

Também estão disponíveis no backend duas alternativas:

1. `recent_messages`: enviar somente as mensagens mais recentes dentro do limite.
2. `new_session`: ignorar o histórico e enviar somente a mensagem atual.

A interface também oferece o botão **Nova conversa**, que executa a segunda ideia localmente, sem persistir dados.

## Estados para demonstrar

- **Carregando:** envie uma mensagem e observe “O modelo está pensando…” enquanto o pedido está em andamento.
- **Limite de requisições:** use um modelo com limite atingido ou simule um retorno HTTP 429 no backend; a interface mostrará a orientação para aguardar ou trocar o modelo.
- **Falha de rede:** desligue a conexão ou bloqueie o endpoint; a interface mostrará “Falha de rede...” sem quebrar a aplicação.
- **Nova sessão:** clique em “Nova conversa” para apagar o histórico que está apenas em memória.

## Estrutura

```text
pre_cp/
├── app.py                    # rotas Flask e catálogo exibido
├── main.py                   # entrada web + compatibilidade CLI
├── core/request_model.py     # cliente OpenRouter, erros e política de contexto
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Observações para a entrega

- Não coloque a chave real no README, no JavaScript ou em commits.
- A política de histórico fica visível na interface e é aplicada no backend, não apenas no navegador.
- Para a captura ou vídeo, demonstre uma conversa normal, uma tela durante carregamento e um erro controlado.
