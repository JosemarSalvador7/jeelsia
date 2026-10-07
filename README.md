# Jeelsia — Assistente Virtual de Conhecimento

Jeelsia é uma assistente de terminal desenvolvida em Python que responde a mensagens em português usando uma base de conhecimento SQLite. O projeto demonstra uma arquitetura leve para processamento de comandos, conversa simples e pesquisa fuzzy de factos, conhecimentos, conselhos e histórias.

## Visão geral

- `main.py`: ponto de entrada da aplicação e loop de conversa no terminal.
- `logica/knowledge_base/knowledge_base.py`: implementa a base de dados SQLite, criação de tabelas e buscas fuzzy usando `rapidfuzz`.
- `logica/msgs/msgs.py`: define mensagens de busca, padrões de conversa, prefixos factuais e respostas padrão.
- `logica/__init__.py`: exporta a classe `KnowledgeBase` e as funções de configuração.
- `IA_integration.md`: documentação complementar sobre uso e potencial das dependências existentes.

## Funcionalidades principais

- loop de conversa interativa no terminal
- respostas a saudações e perguntas comuns
- busca de factos, conhecimentos, conselhos e histórias
- monitoramento de inatividade com mensagens automáticas
- persistência de dados em SQLite (`cerebro.db`)
- fallback para respostas padrão quando não há correspondência

## Requisitos

Recomendado usar Python 3.14 ou superior.

Dependências principais:

- `humanize`
- `rapidfuzz`

Dependências listadas em `pyproject.toml`:

- `humanize>=4.16.0`
- `nltk>=3.10.0`
- `numpy>=2.5.1`
- `pydantic>=2.13.4`
- `rapidfuzz>=3.14.5`
- `scikit-learn>=1.9.0`
- `sqlmodel>=0.0.39`

> Nota: O núcleo atual da aplicação usa `humanize` e `rapidfuzz`. As outras dependências podem ser úteis para evoluções futuras de NLP, validação, modelos e persistência de dados.

## Instalação

1. Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências necessárias:

```bash
python -m pip install humanize rapidfuzz
```

3. Caso queira utilizar todas as dependências listadas em `pyproject.toml`, instale também:

```bash
python -m pip install nltk numpy pydantic scikit-learn sqlmodel
```

## Execução

Execute a assistente no terminal:

```bash
python main.py
```

A aplicação cria automaticamente o ficheiro `cerebro.db` na primeira execução e inicializa as tabelas necessárias.

## Estrutura do projeto

- `main.py`: classe `Jeelsia`, configuração do ambiente, processamento de comandos e loop de interação.
- `logica/__init__.py`: exporta componentes reutilizáveis da lógica do projeto.
- `logica/knowledge_base/knowledge_base.py`: gerencia a base de dados, normalização de texto e pesquisas fuzzies.
- `logica/msgs/msgs.py`: guarda frases e padrões usados pela assistente.
- `IA_integration.md`: documento adicional com sugestões de integração e melhoria.

## Como estender

- Adicionar mais factos, conhecimentos, conselhos e histórias diretamente na base `cerebro.db`.
- Melhorar a deteção de intenções usando `scikit-learn` ou `nltk`.
- Validar entradas com `pydantic` antes de processar mensagens.
- Substituir o uso direto de SQLite por `sqlmodel` para modelos tipados.

## Observações

- As pesquisas usam `rapidfuzz` para avaliar similaridade entre o texto do utilizador e os registos da base.
- O projeto já tem uma base para crescimento em NLP e recuperação de conhecimento.
- Use `IA_integration.md` como guia para integrar bibliotecas adicionais no futuro.
# jeelsia
