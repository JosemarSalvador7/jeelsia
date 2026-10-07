"""
Dados iniciais (seeds) para popular a base de dados do Jeelsia.

Este módulo contém apenas DADOS — listas de dicionários prontas para
inserir nas tabelas criadas por KnowledgeBase.criar_tabelas():
    factos, conhecimentos, conselhos, habilidades, historias
"""

SEED_FACTOS = [
    {
        "topico": "sol",
        "facto": "O Sol é uma estrela de tipo espectral G2V e representa 99,86% da massa do Sistema Solar.",
        "fonte": "NASA",
        "categoria": "astronomia",
    },
    {
        "topico": "sol",
        "facto": "A luz do Sol leva cerca de 8 minutos e 20 segundos para chegar à Terra.",
        "fonte": "NASA",
        "categoria": "astronomia",
    },
    {
        "topico": "lua",
        "facto": "A Lua afasta-se da Terra aproximadamente 3,8 cm por ano.",
        "fonte": "Apollo Laser Ranging",
        "categoria": "astronomia",
    },
    {
        "topico": "agua",
        "facto": "A água é a única substância natural que existe simultaneamente nos três estados: sólido, líquido e gasoso.",
        "fonte": "Enciclopédia",
        "categoria": "ciencia",
    },
    {
        "topico": "corpo humano",
        "facto": "O corpo humano adulto tem cerca de 37,2 trilhões de células.",
        "fonte": "Annals of Human Biology",
        "categoria": "biologia",
    },
    {
        "topico": "cerebro",
        "facto": "O cérebro consome cerca de 20% da energia do corpo, embora represente apenas 2% do seu peso.",
        "fonte": "Nature Reviews Neuroscience",
        "categoria": "biologia",
    },
    {
        "topico": "portugal",
        "facto": "Portugal é o país mais antigo da Europa com fronteiras praticamente inalteradas desde 1139.",
        "fonte": "História",
        "categoria": "geografia",
    },
    {
        "topico": "brasil",
        "facto": "O Brasil é o maior país da América do Sul e o quinto maior do mundo em área territorial.",
        "fonte": "IBGE",
        "categoria": "geografia",
    },
    {
        "topico": "python",
        "facto": "Python foi criado por Guido van Rossum e lançado pela primeira vez em 1991.",
        "fonte": "Documentação oficial",
        "categoria": "tecnologia",
    },
    {
        "topico": "internet",
        "facto": "A World Wide Web foi inventada por Tim Berners-Lee em 1989 no CERN.",
        "fonte": "CERN",
        "categoria": "tecnologia",
    },
]

SEED_CONHECIMENTOS = [
    {
        "pergunta": "qual e a capital de portugal?",
        "resposta": "A capital de Portugal é Lisboa.",
        "fonte": "Geografia",
        "categoria": "geografia",
    },
    {
        "pergunta": "qual e a capital do brasil?",
        "resposta": "A capital do Brasil é Brasília.",
        "fonte": "Geografia",
        "categoria": "geografia",
    },
    {
        "pergunta": "quanto tempo a luz do sol leva para chegar a terra?",
        "resposta": "Aproximadamente 8 minutos e 20 segundos.",
        "fonte": "NASA",
        "categoria": "astronomia",
    },
    {
        "pergunta": "quem inventou o telefone?",
        "resposta": "Alexander Graham Bell patenteou o telefone em 1876.",
        "fonte": "História",
        "categoria": "historia",
    },
    {
        "pergunta": "o que e inteligencia artificial?",
        "resposta": "Inteligência artificial é a área da computação dedicada a criar sistemas capazes de realizar tarefas que normalmente exigem inteligência humana, como aprender, raciocinar e perceber o ambiente.",
        "fonte": "IA_integration.md",
        "categoria": "tecnologia",
    },
    {
        "pergunta": "para que serve o python?",
        "resposta": "Python serve para desenvolvimento web, ciência de dados, automação, inteligência artificial, scripts e muito mais. É conhecido pela sintaxe simples e legível.",
        "fonte": "Documentação oficial",
        "categoria": "tecnologia",
    },
    {
        "pergunta": "quantos planetas tem o sistema solar?",
        "resposta": "O Sistema Solar tem 8 planetas: Mercúrio, Vénus, Terra, Marte, Júpiter, Saturno, Úrano e Neptuno.",
        "fonte": "NASA",
        "categoria": "astronomia",
    },
    {
        "pergunta": "o que e fotossintese?",
        "resposta": "Fotossíntese é o processo pelo qual as plantas convertem luz, água e dióxido de carbono em glicose e oxigênio.",
        "fonte": "Biologia",
        "categoria": "biologia",
    },
]

SEED_CONSELHOS = [
    {
        "problema": "estresse",
        "conselho": "Respira fundo: inspira em 4 segundos, segura 4 e expira em 6. Uma pausa curta já reduz a tensão.",
        "categoria": "bem-estar",
    },
    {
        "problema": "tristeza",
        "conselho": "Fala com alguém de confiança ou escreve o que sentes. Sentimentos guardados pesam mais do que sentimentos partilhados.",
        "categoria": "emocional",
    },
    {
        "problema": "falta de motivacao",
        "conselho": "Divide a tarefa grande em passos pequenos. Concluir um passo minúsculo gera impulso para o próximo.",
        "categoria": "produtividade",
    },
    {
        "problema": "raiva",
        "conselho": "Antes de responder, espera dez segundos. A raiva passa rápido; as palavras ditas ficam.",
        "categoria": "emocional",
    },
    {
        "problema": "ansiedade",
        "conselho": "Foca-te no que podes controlar agora. O resto pertence ao futuro, que ainda não existe.",
        "categoria": "bem-estar",
    },
    {
        "problema": "procrastinacao",
        "conselho": "Usa a regra dos 2 minutos: se demora menos de dois minutos, faz já. O difícil é começar, não continuar.",
        "categoria": "produtividade",
    },
]

SEED_HABILIDADES = [
    {
        "nome": "conversar",
        "descricao": "Bater papo sobre diversos temas, reconhecer emoções e responder com empatia.",
        "exemplo_uso": "jeelsia, como estas hoje?",
    },
    {
        "nome": "pesquisar factos",
        "descricao": "Procurar factos e conhecimentos na base de dados local usando correspondência fuzzy.",
        "exemplo_uso": "conta-me um facto sobre o cerebro",
    },
    {
        "nome": "dar conselhos",
        "descricao": "Sugerir conselhos práticos quando o utilizador descreve um problema.",
        "exemplo_uso": "estou com falta de motivacao, o que faco?",
    },
    {
        "nome": "contar historias",
        "descricao": "Narrar histórias curtas guardadas na base de conhecimento.",
        "exemplo_uso": "conta-me uma historia",
    },
    {
        "nome": "curiosidade",
        "descricao": "Apresentar um facto aleatório escolhido da base de dados.",
        "exemplo_uso": "surpreende-me com uma curiosidade",
    },
]

SEED_HISTORIAS = [
    {
        "titulo": "o menino que contava estrelas",
        "conteudo": (
            "Numa aldeia pequena, um menino subia todas as noites ao telhado para contar estrelas. "
            "Um dia perguntaram-lhe: 'Já acabaste de contar?' Ele respondeu: 'Não, mas hoje aprendi "
            "uma estrela nova.' E assim percebeu que a curiosidade vale mais do que a resposta final."
        ),
        "autor": "Tradição oral",
        "categoria": "inspiradora",
        "origem": "seed",
    },
    {
        "titulo": "a lampada e o oceano",
        "conteudo": (
            "Uma lâmpada acesa à beira-mar achava que iluminava o oceano inteiro. O oceano, sorrindo, "
            "disse: 'Tu iluminas um palmo; eu guardo luzes que ninguém viu.' A lâmpada apagou-se humilde "
            "— e nessa noite, pela primeira vez, o mar brilhou com o reflexo das estrelas."
        ),
        "autor": "Conto popular",
        "categoria": "filosofica",
        "origem": "seed",
    },
    {
        "titulo": "o programador e o bug",
        "conteudo": (
            "Um programador procurava um bug há semanas. Quando finalmente o encontrou, era um ponto e "
            "vírgula fora do lugar. Ele riu e disse: 'Os maiores mistérios escondem as menores respostas.' "
            "Desde então, comenta o código não só para os outros, mas também para si mesmo do futuro."
        ),
        "autor": "Anônimo",
        "categoria": "humor",
        "origem": "seed",
    },
]


def obter_seeds() -> dict:
    """Devolve todos os conjuntos de dados semente num único dicionário."""
    return {
        "factos": SEED_FACTOS,
        "conhecimentos": SEED_CONHECIMENTOS,
        "conselhos": SEED_CONSELHOS,
        "habilidades": SEED_HABILIDADES,
        "historias": SEED_HISTORIAS,
    }


__all__ = [
    "SEED_FACTOS",
    "SEED_CONHECIMENTOS",
    "SEED_CONSELHOS",
    "SEED_HABILIDADES",
    "SEED_HISTORIAS",
    "obter_seeds",
]
