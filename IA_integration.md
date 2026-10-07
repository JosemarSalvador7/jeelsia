# Integração de bibliotecas no projeto Jeelsia

Este documento explica até que ponto as bibliotecas presentes no ficheiro de dependências, mas ainda não exploradas de forma completa, podem fortalecer o projeto da assistente virtual Jeelsia. O objetivo é mostrar não apenas o valor teórico de cada biblioteca, mas também como implementá-las de forma prática, com exemplos simples e realistas.

## 1. Contexto do projeto

O projeto atual já possui uma base sólida para:

- aceitar mensagens do utilizador em linguagem natural;
- responder a comandos básicos;
- pesquisar factos, conselhos e histórias;
- guardar dados em SQLite;
- usar similaridade textual para encontrar respostas relevantes.

No entanto, o projeto ainda pode evoluir bastante em áreas como:

- processamento mais inteligente de texto em português;
- validação de entradas e saídas;
- organização mais robusta dos dados;
- classificação automática de intenções;
- melhoria da experiência de pesquisa e recuperação de conhecimento.

As bibliotecas abaixo podem ajudar exatamente nesses pontos.

---

## 2. Estado atual das dependências

No ficheiro de dependências existem bibliotecas que já estão a ser usadas e outras que ainda podem ser integradas com grande benefício.

### Bibliotecas já usadas

- rapidfuzz: já usada para comparar similaridade entre frases e perguntas.
- humanize: já usada para formatar tempos e mensagens de inatividade.

### Bibliotecas com potencial ainda não explorado

- nltk: processamento de linguagem natural e normalização de texto.
- numpy: cálculo numérico e manipulação eficiente de vetores.
- scikit-learn: classificação, clustering e modelos de aprendizagem automática.
- pydantic: validação de dados e modelos de entrada/saída.
- sqlmodel: gestão de dados com modelos tipados e integração com SQLAlchemy.

---

## 3. Até que ponto estas bibliotecas podem ajudar?

### 3.1 NLTK

Impacto: alto para melhorar o entendimento de texto.

A biblioteca nltk pode ajudar o projeto a:

- tokenizar frases em português;
- remover palavras pouco úteis, como artigos e preposições;
- stemizar ou lematizar palavras;
- melhorar o processamento de perguntas e comandos.

Isso é especialmente útil porque a assistente recebe texto livre. Com NLTK, o sistema pode analisar melhor o conteúdo das mensagens antes de procurar uma resposta.

#### Exemplo mais focado no projeto

```python
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from logica.msgs.msgs import prefixos_factuais


def preprocessar_mensagem(mensagem: str) -> list[str]:
    tokens = word_tokenize(mensagem, language="portuguese")
    stop_words = set(stopwords.words("portuguese"))
    return [
        token.lower()
        for token in tokens
        if token.lower() not in stop_words
        and re.match(r"^[a-záéíóúãõç]+$", token.lower())
    ]


mensagem = "me explica sobre a base de dados do Jeelsia"
prefixos = prefixos_factuais()
palavras = preprocessar_mensagem(mensagem)

print(palavras)
print(any(prefixo in mensagem.lower() for prefixo in prefixos))
```

#### Como isso pode ser usado no projeto

Este tipo de limpeza poderia ser usado dentro do fluxo de [main.py](main.py) antes de chamar os métodos de busca da classe `KnowledgeBase`. Em vez de comparar a frase inteira, o sistema passaria a analisar apenas os termos mais relevantes, o que melhora a correspondência com os dados guardados em [logica/knowledge_base/knowledge_base.py](logica/knowledge_base/knowledge_base.py).

### 3.2 NumPy

Impacto: médio, mas muito útil para otimização e manipulação de dados.

NumPy pode ajudar a:

- trabalhar com listas de valores numéricos de forma mais eficiente;
- criar vetores de pontuações de confiança;
- comparar várias respostas em lote;
- preparar dados para modelos de aprendizagem automática.

Embora não seja a biblioteca principal para uma aplicação simples, ela torna o código mais performante e prepara o projeto para evoluir.

#### Exemplo mais focado no projeto

```python
import numpy as np

candidatos = [
    {"resposta": "Resposta curta", "similaridade": 72},
    {"resposta": "Resposta mais completa", "similaridade": 91},
    {"resposta": "Resposta relacionada", "similaridade": 85},
]

pontuacoes = np.array([item["similaridade"] for item in candidatos])
melhor_indice = int(np.argmax(pontuacoes))

print(candidatos[melhor_indice]["resposta"])
```

#### Como isso pode ser usado no projeto

No fluxo atual da assistente, depois de usar métodos como `pesquisar_conhecimento_qradio` ou `pesquisar_factos_qradio`, o NumPy poderia ajudar a escolher a melhor resposta entre várias hipóteses de resultados. Isto é útil quando a base de conhecimento devolve mais do que uma possibilidade relevante.

### 3.3 scikit-learn

Impacto: alto para evolução da assistente para um sistema mais inteligente.

Esta biblioteca pode permitir que o projeto:

- classifique automaticamente intenções do utilizador;
- aprenda a distinguir perguntas de saudação, pedido de informação, reclamação ou agradecimento;
- melhore a recuperação de informação com modelos mais sofisticados;
- crie sistemas de recomendação internos com base em padrões.

É talvez a biblioteca com maior potencial de crescimento do projeto.

#### Exemplo mais focado no projeto

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Inspirado no estilo de mensagens usado em logica/msgs/msgs.py
textos_treino = [
    "olá, tudo bem",
    "que horas são",
    "me fala sobre o projeto",
    "quem criou você",
]
rotulos_treino = ["saudacao", "hora", "pergunta", "identidade"]

vectorizer = TfidfVectorizer()
X_treino = vectorizer.fit_transform(textos_treino)

modelo = LogisticRegression(max_iter=400)
modelo.fit(X_treino, rotulos_treino)

mensagem_nova = ["bom dia"]
predicao = modelo.predict(vectorizer.transform(mensagem_nova))
print(predicao[0])
```

#### Como isso pode ser usado no projeto

A assistente poderia usar este modelo para decidir se uma mensagem deve seguir para a lógica de conversa em [main.py](main.py) ou para a busca de conhecimento em [logica/knowledge_base/knowledge_base.py](logica/knowledge_base/knowledge_base.py). Isto torna o sistema mais inteligente do que depender apenas de comparações de similaridade.

### 3.4 Pydantic

Impacto: alto para organização e segurança do código.

Pydantic é excelente para:

- validar dados recebidos;
- garantir que campos como texto, categoria ou fonte tenham o formato certo;
- evitar erros causados por entradas inesperadas;
- deixar o código mais claro e mais fácil de manter.

#### Exemplo mais focado no projeto

```python
from pydantic import BaseModel, Field


class MensagemEntrada(BaseModel):
    texto: str = Field(min_length=1)
    origem: str = "terminal"
    prioridade: int = Field(default=1, ge=1, le=5)


mensagem = MensagemEntrada(texto="me fala sobre o projeto", prioridade=3)
print(mensagem.texto)
print(mensagem.prioridade)
```

#### Como isso pode ser usado no projeto

Este modelo seria muito útil no método `responder()` de [main.py](main.py), porque permitiria validar a entrada antes de a enviar para a lógica de conversa ou para a pesquisa na base de conhecimento. Assim, mensagens vazias, muito curtas ou mal estruturadas poderiam ser tratadas com mais segurança.

### 3.5 SQLModel

Impacto: alto para evoluir a camada de dados.

SQLModel permite criar modelos de dados de forma mais elegante e organizada. Em vez de trabalhar apenas com SQL bruto, o projeto pode passar a usar objetos e estruturas tipadas.

Isso ajuda a:

- organizar melhor os dados de conhecimento;
- reduzir erros ao inserir registos;
- facilitar futuras expansões do projeto;
- tornar a base de dados mais fácil de manter.

#### Exemplo mais focado no projeto

```python
from sqlmodel import SQLModel, Field, Session, create_engine


class Fato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topico: str
    facto: str
    fonte: str | None = None


class Conhecimento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pergunta: str
    resposta: str
    categoria: str | None = None


engine = create_engine("sqlite:///jeelsia_modelos.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(
        Conhecimento(pergunta="qual é o teu nome", resposta="Sou Jeelsia")
    )
    session.commit()
```

#### Como isso pode ser usado no projeto

Este tipo de abordagem encaixa muito bem com as tabelas já usadas em [logica/knowledge_base/knowledge_base.py](logica/knowledge_base/knowledge_base.py), como `factos`, `conhecimentos` e `conselhos`. Em vez de trabalhar apenas com SQL bruto, o projeto podia passar a usar modelos declarativos para organizar a base de dados de forma mais limpa.

---

## 4. Estratégia recomendada para integração

A forma mais eficiente de evoluir o projeto é seguir uma estratégia por fases.

### Fase 1: melhorar o processamento de texto

- integrar nltk para normalizar e limpar mensagens;
- usar stopwords e tokenização em português;
- combinar essa lógica com a busca atual por similaridade.

### Fase 2: fortalecer a validação de entradas

- aplicar pydantic para garantir que as mensagens e os dados recebidos estejam corretos;
- evitar erros inesperados ao processar perguntas do utilizador.

### Fase 3: organizar a base de conhecimento

- migrar parte da camada de dados para sqlmodel;
- criar modelos para factos, conhecimentos e conselhos;
- manter compatibilidade com a base SQLite atual.

### Fase 4: adicionar inteligência automática

- usar scikit-learn para classificar intenções;
- combinar com numpy para processar e comparar múltiplas hipóteses de resposta;
- criar um sistema mais próximo de um assistente inteligente, e não apenas de um chatbot baseado em regras.

---

## 5. Plano de implementação passo a passo

A forma mais segura de evoluir o projeto é implementar as bibliotecas de forma incremental, sem quebrar o comportamento atual da assistente.

### Passo 1: preparar o ambiente

- verificar se as dependências estão instaladas corretamente;
- confirmar que o projeto continua a executar com [main.py](main.py);
- criar um ramo de desenvolvimento para testes;
- manter a base atual de dados [cerebro.db](cerebro.db) intacta durante a transição.

### Passo 2: integrar NLTK para processamento de texto

- adicionar suporte para tokenização e remoção de palavras irrelevantes;
- criar uma função auxiliar para limpar mensagens antes da busca;
- aplicar essa função no fluxo de entrada em [main.py](main.py);
- comparar os resultados com o comportamento atual para ver se a resposta melhora.

Exemplo de objetivo:

- transformar mensagens como “me explica sobre o projeto” em termos mais simples para pesquisa.

### Passo 3: adicionar validação com Pydantic

- criar modelos para representar entradas do utilizador;
- validar mensagens antes de processá-las;
- impedir que mensagens vazias ou mal formadas causem erros na lógica principal;
- manter as respostas da assistente mais consistentes.

Exemplo de objetivo:

- garantir que pedidos muito curtos ou sem conteúdo não sejam tratados como perguntas válidas.

### Passo 4: melhorar a seleção de respostas com NumPy

- usar arrays numéricos para comparar várias hipóteses de resposta;
- escolher a melhor resposta com base em pontuações de similaridade;
- testar esta lógica sobre os resultados já retornados por [logica/knowledge_base/knowledge_base.py](logica/knowledge_base/knowledge_base.py).

Exemplo de objetivo:

- quando existirem várias respostas possíveis, escolher a mais relevante.

### Passo 5: introduzir scikit-learn para classificação de intenções

- criar um pequeno conjunto de exemplos de treino com frases típicas do projeto;
- classificar mensagens em categorias como saudação, pergunta, identidade ou conversa;
- ligar esta classificação ao fluxo principal em [main.py](main.py);
- usar a classificação para decidir se a mensagem deve ir para conversa ou para a base de conhecimento.

Exemplo de objetivo:

- distinguir mensagens como “bom dia” de perguntas como “me conta sobre o projeto”.

### Passo 6: reorganizar a camada de dados com SQLModel

- definir modelos para factos, conhecimentos e conselhos;
- migrar gradualmente os dados para modelos mais estruturados;
- manter compatibilidade com a base SQLite atual enquanto a migração acontece;
- reduzir a complexidade do código de gestão de dados.

Exemplo de objetivo:

- passar a trabalhar com objetos Python mais claros em vez de SQL manualmente.

### Passo 7: validar o projeto completo

- testar o sistema com mensagens simples e mais complexas;
- comparar respostas antes e depois da integração;
- corrigir erros de compatibilidade;
- documentar as mudanças para futuras melhorias.

---

## 6. Conclusão

As bibliotecas ainda não implementadas podem ajudar o projeto de forma muito significativa, especialmente em quatro áreas principais:

1. melhor compreensão de texto em português;
2. validação e organização mais segura de dados;
3. evolução para uma arquitetura mais profissional;
4. introdução de inteligência artificial básica e classificação de intenções.

Em termos práticos, o projeto pode passar de uma assistente baseada essencialmente em regras para uma solução mais inteligente, robusta e preparada para crescer.

A recomendação mais equilibrada é começar com NLTK e Pydantic, depois evoluir para SQLModel e, por fim, introduzir scikit-learn com NumPy para criar modelos de classificação e análise mais avançados.
